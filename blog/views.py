from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.views.decorators.http import require_POST

from .models import Post, PerfilUsuario
from .forms import PostForm, ComentarioForm


# =====================================================
# LISTAR PUBLICACIONES
# =====================================================

def lista_posts(request):
    posts = Post.objects.all().order_by("-fecha_publicacion")

    return render(
        request,
        "blog/lista_posts.html",
        {"posts": posts}
    )


# =====================================================
# VER DETALLE DE PUBLICACION Y COMENTARIOS
# =====================================================

def detalle_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Incrementar contador de visitas
    post.vistas += 1
    post.save(update_fields=["vistas"])

    # Obtener comentarios
    comentarios = post.comentarios.all().order_by("-fecha")

    # Procesar comentarios
    if request.method == "POST":

        if not request.user.is_authenticated:
            return redirect("login")

        form = ComentarioForm(request.POST)

        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.post = post
            nuevo.autor_usuario = request.user
            nuevo.save()

            return redirect(
                "detalle_post",
                slug=post.slug
            )

    else:
        form = ComentarioForm()

    # Comprobar si el usuario es administrador
    es_administrador = (
        request.user.is_authenticated
        and (
            request.user.is_superuser
            or request.user.groups.filter(
                name="Administrador"
            ).exists()
        )
    )

    # Mostrar detalle de la publicacion
    return render(
        request,
        "blog/detalle_post.html",
        {
            "post": post,
            "comentarios": comentarios,
            "form": form,
            "es_administrador": es_administrador,
        }
    )


# =====================================================
# CREAR PUBLICACION (Solo requiere estar autenticado)
# =====================================================

@login_required
def crear_post(request):

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            nuevo = form.save(commit=False)
            nuevo.autor = request.user
            nuevo.save()

            return redirect(
                "detalle_post",
                slug=nuevo.slug
            )

    else:
        form = PostForm()

    return render(
        request,
        "blog/crear_post.html",
        {"form": form}
    )


# =====================================================
# EDITAR PUBLICACION (El autor o el administrador)
# =====================================================

@login_required
def editar_post(request, slug):

    post = get_object_or_404(Post, slug=slug)

    es_administrador = (
        request.user.is_superuser
        or request.user.groups.filter(
            name="Administrador"
        ).exists()
    )

    es_autor = post.autor_id == request.user.pk

    if not es_administrador and not es_autor:
        raise PermissionDenied(
            "No tienes permiso para editar esta publicacion."
        )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post
        )

        if form.is_valid():
            form.save()

            return redirect(
                "detalle_post",
                slug=post.slug
            )

    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/crear_post.html",
        {
            "form": form,
            "editar": True,
        }
    )


# =====================================================
# ELIMINAR PUBLICACION (El autor o el administrador)
# =====================================================

@login_required
@require_POST
def eliminar_post(request, slug):

    post = get_object_or_404(Post, slug=slug)

    es_administrador = (
        request.user.is_superuser
        or request.user.groups.filter(
            name="Administrador"
        ).exists()
    )

    es_autor = post.autor_id == request.user.pk

    if not es_administrador and not es_autor:
        raise PermissionDenied(
            "No tienes permiso para eliminar esta publicacion."
        )

    post.delete()

    return redirect("lista_posts")


# =====================================================
# PERFIL DE USUARIO
# =====================================================

@login_required
def perfil_usuario(request):

    perfil, creado = PerfilUsuario.objects.get_or_create(
        usuario=request.user
    )

    return render(
        request,
        "blog/perfil.html",
        {
            "perfil": perfil,
        }
    )