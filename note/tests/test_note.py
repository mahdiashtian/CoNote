import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework import status

from note.models import Note, NoteBook

User = get_user_model()


@pytest.fixture()
def list_note(api_client):
    notebook_obj = baker.make(NoteBook)
    objs = baker.make(Note, notebook=notebook_obj, _quantity=18)

    def do_list_note(user=None, user_perm=None):
        if user:
            notebook_obj.user = user
            notebook_obj.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, notebook_obj)
        url = reverse('note:note-list')
        response = api_client.get(url, {'notebook': notebook_obj.id})
        return response

    return do_list_note


@pytest.fixture()
def create_note(api_client):
    obj_notebook = baker.make(NoteBook)
    sample = {
        'title': 'Test Title',
        'content': 'Test Content',
        'placement': 1,
        'notebook': obj_notebook.id
    }

    def do_create_note(test_payload=None, user=None):
        if test_payload is None:
            test_payload = sample
        if user:
            obj_notebook.user = user
            obj_notebook.save()
        data = {**sample, **test_payload}
        url = reverse('note:note-list')
        return api_client.post(url, data=data)

    return do_create_note


@pytest.fixture()
def update_note(api_client):
    obj_notebook = baker.make(NoteBook)
    sample = {
        'title': 'Test Title',
        'content': 'Test Content',
        'placement': 1,
        'notebook': obj_notebook.id
    }
    obj = baker.make(Note, notebook=obj_notebook)

    def do_update_note(test_payload=None, user=None, user_perm=None, pk=obj.id):
        if test_payload is None:
            test_payload = sample
        if user:
            obj_notebook.user = user
            obj_notebook.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, obj_notebook)
        data = {**sample, **test_payload}
        url = reverse('note:note-detail', kwargs={'pk': pk})
        return api_client.put(url, data=data)

    return do_update_note


@pytest.fixture()
def destroy_note(api_client):
    obj = baker.make(Note)

    def do_destroy_note(user=None, user_perm=None, pk=obj.id):
        if user:
            obj.notebook.user = user
            obj.notebook.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, obj.notebook)
        url = reverse('note:note-detail', kwargs={'pk': pk})
        return api_client.delete(url)

    return do_destroy_note


@pytest.mark.django_db
class TestListNote:
    def test_list_note_if_user_is_authenticated_and_is_owner_return_200(self, authenticate, list_note):
        _, user = authenticate()
        response = list_note(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_list_note_if_user_is_authenticated_and_has_perm_return_200(self, authenticate, list_note):
        _, user = authenticate()
        response = list_note(user_perm=user)
        assert response.status_code == status.HTTP_200_OK

    def test_list_note_if_user_is_not_authenticated_return_401(self, list_note):
        response = list_note()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_note_if_user_is_not_owner_and_not_perm_return_403(self, authenticate, list_note):
        _, user = authenticate()
        response = list_note()
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCreateNote:
    def test_create_note_if_user_is_authenticated_and_is_valid_data_return_201(self, authenticate, create_note):
        _, user = authenticate()
        response = create_note(user=user)
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_note_if_user_is_not_authenticated_return_401(self, create_note):
        response = create_note()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_note_if_user_is_authenticated_and_is_invalid_data_return_400(self, authenticate, create_note):
        _, user = authenticate()
        response = create_note({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdateNote:
    def test_update_note_if_user_is_authenticated_and_is_owner_return_200(self, authenticate, update_note):
        _, user = authenticate()
        response = update_note(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_update_note_if_user_is_authenticated_and_has_perm_return_403(self, authenticate, update_note):
        _, user = authenticate()
        response = update_note(user_perm=user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_note_if_user_is_not_authenticated_return_401(self, update_note):
        response = update_note()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_if_user_is_authenticated_and_is_invalid_data_return_400(self, authenticate, update_note):
        _, user = authenticate()
        response = update_note({'title': ''}, user=user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_note_if_user_is_authenticated_and_is_owner_and_is_invalid_pk_return_404(self, authenticate,
                                                                                            update_note):
        _, user = authenticate()
        response = update_note(user=user, pk=12312)
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDestroyNote:
    def test_destroy_note_if_user_is_authenticated_and_is_owner_return_204(self, authenticate, destroy_note):
        _, user = authenticate()
        response = destroy_note(user=user)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_destroy_note_if_user_is_authenticated_and_has_perm_return_403(self, authenticate, destroy_note):
        _, user = authenticate()
        response = destroy_note(user_perm=user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_destroy_note_if_user_is_not_authenticated_return_401(self, destroy_note):
        response = destroy_note()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_destroy_if_user_is_authenticated_and_is_invalid_pk_return_404(self, authenticate, destroy_note):
        _, user = authenticate()
        response = destroy_note(user=user, pk=12312)
        assert response.status_code == status.HTTP_404_NOT_FOUND
