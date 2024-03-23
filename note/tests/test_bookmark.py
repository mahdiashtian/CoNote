import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework import status

from note.models import NoteBook, Note, BookMark

User = get_user_model()


@pytest.fixture()
def create_bookmark(api_client):
    obj_notebook = baker.make(NoteBook)
    obj_note = baker.make(Note, notebook=obj_notebook)
    sample = {
        'note': obj_note.id,
    }

    def do_create_bookmark(test_payload=None, user=None, user_perm=None):
        if test_payload is None:
            test_payload = sample
        if user:
            obj_notebook.user = user
            obj_notebook.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, obj_notebook)
        data = {**sample, **test_payload}
        url = reverse('note:bookmark-list')
        return api_client.post(url, data)

    return do_create_bookmark


@pytest.fixture()
def list_bookmark(api_client):
    objs = baker.make(BookMark, _quantity=5)

    def do_list_bookmark(user=None):
        url = reverse('note:bookmark-list')
        return api_client.get(url)

    return do_list_bookmark


@pytest.fixture()
def destroy_bookmark(api_client):
    obj = baker.make(BookMark)

    def do_destroy_bookmark(user=None, pk=obj.id):
        if user:
            obj.user = user
            obj.save()
        url = reverse('note:bookmark-detail', kwargs={'pk': pk})
        return api_client.delete(url)

    return do_destroy_bookmark


@pytest.mark.django_db
class TestCreateBookmark:
    def test_create_bookmark_if_user_is_authenticated_and_valid_data_return_201(self, create_bookmark, authenticate):
        _, user = authenticate()
        response = create_bookmark(user=user)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_bookmark_if_user_is_authenticated_and_has_perm_and_valid_data_201(self, create_bookmark,
                                                                                      authenticate):
        _, users = authenticate()
        response = create_bookmark(user_perm=users)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_bookmark_if_user_is_authenticated_and_invalid_data_return_400(self, create_bookmark, authenticate):
        _, user = authenticate()
        response = create_bookmark({'note': 100010101}, user=user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_bookmark_if_user_is_authenticated_and_not_perm_return_400(self, create_bookmark, authenticate):
        _, user = authenticate()
        response = create_bookmark()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_bookmark_if_user_is_not_authenticated_return_401(self, create_bookmark):
        response = create_bookmark()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListBookmark:
    def test_list_bookmark_if_user_is_authenticated_return_200(self, list_bookmark, authenticate):
        _, user = authenticate()
        response = list_bookmark(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_list_bookmark_if_user_is_not_authenticated_return_401(self, list_bookmark):
        response = list_bookmark()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDestroyBookmark:
    def test_destroy_bookmark_if_user_is_authenticated_and_valid_data_return_204(self, destroy_bookmark, authenticate):
        _, user = authenticate()
        response = destroy_bookmark(user=user)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_destroy_bookmark_if_user_is_authenticated_and_invalid_pk_return_404(self, destroy_bookmark,
                                                                                 authenticate):
        _, user = authenticate()
        response = destroy_bookmark(user=user, pk=100000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_bookmark_if_user_is_authenticated_and_not_perm_return_404(self, destroy_bookmark, authenticate):
        _, user = authenticate()
        response = destroy_bookmark()
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_bookmark_if_user_is_not_authenticated_return_401(self, destroy_bookmark):
        response = destroy_bookmark()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
