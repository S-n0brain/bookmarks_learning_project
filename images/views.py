from re import L

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models.manager import BaseManager
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from images.forms import ImageCreateForm
from images.models import Image


@login_required
def image_create(request: HttpRequest) -> HttpResponseRedirect | HttpResponse:
    if request.method == "POST":
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            new_image = form.save(commit=False)
            new_image.user = request.user
            new_image.save()
            messages.success(request=request, message="Image added successfully")
            return redirect(to=new_image.get_absolute_url())
    form = ImageCreateForm(data=request.GET)
    return render(
        request, "images/image/create.html", {"section": "images", "form": form}
    )


def image_detail(request: HttpRequest, id: int, slug: str):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request, "images/image/detail.html", {"image": image})


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
        images = paginator.page(1) # type: ignore
    except EmptyPage:
        if images_only:
            # Если AJAX-запрос и страница вне диапазона,
            # то вернуть пустую страницу
            return HttpResponse("")
        images = paginator.page(paginator.num_pages) # type: ignore
    if images_only:
        return render(
            request,
            "images/image/list_images.html",
            {"section": "images", "images": images},
        )
    return render(
        request, "images/image/list.html", {"section": "images", "images": images}
    )
