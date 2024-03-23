import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework import status

from note.models import NoteBook, Note, Comment

User = get_user_model()


@pytest.fixture()
def create_comment(api_client):
    obj_notebook = baker.make(NoteBook)
    obj_note = baker.make(Note, notebook=obj_notebook)
    sample = {
        'note': obj_note.id,
        'content': 'Hi'
    }

    def do_create_comment(test_payload=None, user=None, user_perm=None):
        if test_payload is None:
            test_payload = sample
        if user:
            obj_notebook.user = user
            obj_notebook.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, obj_notebook)
        data = {**sample, **test_payload}
        url = reverse('note:comment-list')
        return api_client.post(url, data)

    return do_create_comment


@pytest.fixture()
def list_comment(api_client):
    objs = baker.make(Comment, _quantity=5)

    def do_list_comment(user=None):
        url = reverse('note:comment-list')
        return api_client.get(url)

    return do_list_comment


@pytest.fixture()
def destroy_comment(api_client):
    obj = baker.make(Comment)

    def do_destroy_comment(user=None, pk=obj.id):
        if user:
            obj.user = user
            obj.save()
        url = reverse('note:comment-detail', kwargs={'pk': pk})
        return api_client.delete(url)

    return do_destroy_comment


@pytest.mark.django_db
class TestCreateBookmark:
    def test_create_comment_if_user_is_authenticated_and_valid_data_return_201(self, create_comment, authenticate):
        _, user = authenticate()
        response = create_comment(user=user)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_comment_if_user_is_authenticated_and_has_perm_and_valid_data_201(self, create_comment,
                                                                                     authenticate):
        _, users = authenticate()
        response = create_comment(user_perm=users)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_comment_if_user_is_authenticated_and_invalid_data_return_400(self, create_comment, authenticate):
        _, user = authenticate()
        response = create_comment({'note': 100010101}, user=user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_if_user_is_authenticated_and_not_perm_return_400(self, create_comment, authenticate):
        _, user = authenticate()
        response = create_comment()
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_comment_if_user_is_not_authenticated_return_401(self, create_comment):
        response = create_comment()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListBookmark:
    def test_list_comment_if_user_is_authenticated_return_200(self, list_comment, authenticate):
        _, user = authenticate()
        response = list_comment(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_list_comment_if_user_is_not_authenticated_return_401(self, list_comment):
        response = list_comment()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestDestroyBookmark:
    def test_destroy_comment_if_user_is_authenticated_and_valid_data_return_204(self, destroy_comment, authenticate):
        _, user = authenticate()
        response = destroy_comment(user=user)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_destroy_comment_if_user_is_authenticated_and_invalid_pk_return_404(self, destroy_comment,
                                                                                authenticate):
        _, user = authenticate()
        response = destroy_comment(user=user, pk=100000)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_comment_if_user_is_authenticated_and_not_perm_return_404(self, destroy_comment, authenticate):
        _, user = authenticate()
        response = destroy_comment()
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_destroy_comment_if_user_is_not_authenticated_return_401(self, destroy_comment):
        response = destroy_comment()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
