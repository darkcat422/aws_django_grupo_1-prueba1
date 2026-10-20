from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import Categoria, Post


class SlugUnicoTests(TestCase):
    def test_posts_con_titulo_repetido_reciben_slugs_distintos(self):
        autor = User.objects.create_user(username="autor", password="password-segura")

        primero = Post.objects.create(titulo="Mi mascota", contenido="Texto", autor=autor)
        segundo = Post.objects.create(titulo="Mi mascota", contenido="Otro texto", autor=autor)

        self.assertEqual(primero.slug, "mi-mascota")
        self.assertEqual(segundo.slug, "mi-mascota-2")

    def test_categorias_con_nombre_repetido_reciben_slugs_distintos(self):
        primera = Categoria.objects.create(nombre="Cuidados!")
        segunda = Categoria.objects.create(nombre="Cuidados")

        self.assertEqual(primera.slug, "cuidados")
        self.assertEqual(segunda.slug, "cuidados-2")


class DetallePostTests(TestCase):
    def test_autor_ve_acciones_de_edicion_y_eliminacion(self):
        autor = User.objects.create_user(username="autor", password="password-segura")
        post = Post.objects.create(titulo="Mi mascota", contenido="Texto", autor=autor)
        self.client.force_login(autor)

        response = self.client.get(reverse("detalle_post", args=[post.slug]))

        self.assertContains(response, reverse("editar_post", args=[post.slug]))
        self.assertContains(response, reverse("eliminar_post", args=[post.slug]))
