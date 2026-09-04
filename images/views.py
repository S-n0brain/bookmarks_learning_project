import redis
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.manager import BaseManager
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from actions.utils import create_action
from images.forms import ImageCreateForm
from images.models import Image

r = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True,
)


@login_required
def image_create(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.method == "POST":
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            create_action(user=request.user, verb="bookmarked image", target=new_image)
            messages.success(request=request, message="Image added successfully")
            return redirect(to=new_image.get_absolute_url())
    form = ImageCreateForm(data=request.GET)
    return render(
        request, "images/image/create.html", {"section": "images", "form": form}
    )


def image_detail(request: HttpRequest, id: int, slug: str):
    image = get_object_or_404(Image, id=id, slug=slug)
    pipe = r.pipeline()
    pipe.incr(name=f"image:{image.id}:views")
    pipe.zincrby(name="image_ranking", amount=1, value=image.id)
    total_views = pipe.execute()
    return render(
        request,
        "images/image/detail.html",
        {"section": "images", "image": image, "total_views": total_views[0]},
    )


@login_required
@require_POST
def image_like(request: HttpRequest):
    image_id = request.POST.get("id")
    action = request.POST.get("action")
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(request.user)
                create_action(user=request.user, verb="likes", target=image)
            else:
                image.users_like.remove(request.user)
            return JsonResponse(data={"status": "ok"})
        except (Image.DoesNotExist, Image.MultipleObjectsReturned):
            pass
        return JsonResponse(data={"status": "error"})


@login_required
def image_list(request: HttpRequest):
    images: BaseManager = Image.objects.all()
    paginator = Paginator(object_list=images, per_page=8)
    page = request.GET.get("page")
    images_only = request.GET.get("images_only")
    try:
        images = paginator.page(page)  # type: ignore
    except PageNotAnInteger:
        # Если страница не является целым числом,
        # то доставить первую страницу
        images = paginator.page(1)  # type: ignore
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона,
            # то вернуть пустую страницу
            return HttpResponse("")
        images = paginator.page(paginator.num_pages)  # type: ignore
    if images_only:
        return render(
            request,
            "images/image/list_images.html",
            {"section": "images", "images": images},
        )
    return render(
        request, "images/image/list.html", {"section": "images", "images": images}
    )


@login_required
def image_ranking(request: HttpRequest):
    ranking_data = r.zrange(
        name="image_ranking", start=0, end=-1, desc=True, withscores=True
    )
    # Словарь {id_картинки: количество_просмотров}
    image_views = {int(img_id): score for img_id, score in ranking_data}

    most_viewed = []
    if image_views:
        images = list(Image.objects.filter(id__in=image_views.keys()))
        images.sort(key=lambda img: image_views[img.id], reverse=True)
        most_viewed = [(img, image_views[img.id]) for img in images]
    return render(
        request,
        "images/image/ranking.html",
        {"section": "ranking_images", "most_viewed": most_viewed},
    )
