import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from guardian.shortcuts import assign_perm
from model_bakery import baker
from rest_framework import status

from note.models import NoteBook

User = get_user_model()


@pytest.fixture()
def assign_perm_notebook(api_client):
    obj = baker.make(NoteBook)
    sample = {
        "user": baker.make(User).id
    }

    def do_assign_perm_notebook(user=None, note_book=obj, test_payload=None, user_perm=None):
        if user:
            note_book.user = user
            note_book.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, note_book)
        if test_payload is None:
            test_payload = sample

        data = {**sample, **test_payload}

        url = reverse('note:notebook-assign-perm', kwargs={'pk': note_book.id})
        return api_client.post(url, data=data)

    return do_assign_perm_notebook


@pytest.fixture()
def remove_perm_notebook(api_client):
    obj = baker.make(NoteBook)
    sample = {
        "user": baker.make(User).id
    }

    def do_remove_perm_notebook(user=None, note_book=obj, test_payload=None, user_perm=None):
        if user:
            note_book.user = user
            note_book.save()
        if user_perm:
            assign_perm('note.view_notebook', user_perm, note_book)
        if test_payload is None:
            test_payload = sample

        data = {**sample, **test_payload}

        url = reverse('note:notebook-remove-perm', kwargs={'pk': note_book.id})
        return api_client.post(url, data=data)

    return do_remove_perm_notebook


@pytest.fixture()
def create_notebook(api_client):
    sample = {
        "title": "notebook title",
        "description": "notebook description"
    }

    def do_create_notebook(test_payload=None):
        if test_payload is None:
            test_payload = sample
        data = {**sample, **test_payload}
        url = reverse('note:notebook-list')
        return api_client.post(url, data=data)

    return do_create_notebook


@pytest.fixture()
def update_notebook(api_client):
    sample = {
        "title": "notebook title",
        "description": "notebook description"
    }
    obj = baker.make(NoteBook)

    def do_update_notebook(pk=obj.id, user=None, note_book=obj, user_prem=None, test_payload=None):
        if user:
            note_book.user = user
            note_book.save()
        if user_prem:
            assign_perm('note.view_notebook', user_prem, note_book)
        if test_payload is None:
            test_payload = sample
        data = {**sample, **test_payload}
        url = reverse('note:notebook-detail', kwargs={'pk': pk})
        return api_client.patch(url, data=data)

    return do_update_notebook


@pytest.fixture()
def list_notebook(api_client):
    objs = baker.make(NoteBook, _quantity=18)

    def do_list_notebook():
        url = reverse('note:notebook-list')
        return api_client.get(url)

    return do_list_notebook


@pytest.fixture()
def retrieve_notebook(api_client):
    obj = baker.make(NoteBook)

    def do_retrieve_notebook(pk=obj.id, user=None, note_book=obj, user_prem=None):
        if user:
            note_book.user = user
            note_book.save()
        if user_prem:
            assign_perm('note.view_notebook', user_prem, note_book)
        url = reverse('note:notebook-detail', kwargs={'pk': pk})
        return api_client.get(url)

    return do_retrieve_notebook


@pytest.fixture()
def remove_notebook(api_client):
    obj = baker.make(NoteBook)

    def do_remove_notebook(pk=obj.id, user=None, note_book=obj, user_prem=None):
        if user:
            note_book.user = user
            note_book.save()
        if user_prem:
            assign_perm('note.view_notebook', user_prem, note_book)
        url = reverse('note:notebook-detail', kwargs={'pk': pk})
        return api_client.delete(url)

    return do_remove_notebook


@pytest.mark.django_db
class TestCreateNoteBook:
    def test_create_notebook_if_data_is_valid_return_201(self, create_notebook, authenticate):
        authenticate()
        response = create_notebook()
        assert response.status_code == status.HTTP_201_CREATED

    def test_create_notebook_if_data_is_invalid_return_400(self, create_notebook, authenticate):
        authenticate()
        response = create_notebook({"title": ""})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_notebook_if_user_is_not_authenticated_return_401(self, create_notebook):
        response = create_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestListNoteBook:
    def test_list_notebook_if_user_is_authenticated_return_200(self, authenticate, list_notebook):
        authenticate()
        response = list_notebook()
        assert response.status_code == status.HTTP_200_OK

    def test_list_notebook_if_user_is_not_authenticated_return_401(self, list_notebook):
        response = list_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRetrieveNoteBook:
    def test_retrieve_notebook_if_user_is_authenticated_and_owner_return_200(self, authenticate, retrieve_notebook):
        _, user = authenticate()
        response = retrieve_notebook(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_notebook_if_user_is_authenticated_and_has_perm_return_200(self, authenticate, retrieve_notebook):
        _, user = authenticate()
        response = retrieve_notebook(user_prem=user)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_notebook_if_user_is_not_authenticated_return_401(self, retrieve_notebook):
        response = retrieve_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_notebook_if_user_is_not_owner_and_not_perm_return_404(self, authenticate, retrieve_notebook):
        authenticate()
        response = retrieve_notebook()
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestRemoveNoteBook:
    def test_remove_notebook_if_user_is_authenticated_and_owner_return_204(self, authenticate, remove_notebook):
        _, user = authenticate()
        response = remove_notebook(user=user)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_retrieve_notebook_if_user_is_authenticated_and_has_perm_return_200(self, authenticate, retrieve_notebook):
        _, user = authenticate()
        response = retrieve_notebook(user_prem=user)
        assert response.status_code == status.HTTP_200_OK

    def test_remove_notebook_if_user_is_not_authenticated_return_401(self, remove_notebook):
        response = remove_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remove_notebook_if_user_is_not_owner_return_404(self, authenticate, remove_notebook):
        authenticate()
        response = remove_notebook()
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestUpdateNoteBook:
    def test_update_notebook_if_user_is_authenticated_and_owner_return_200(self, authenticate, update_notebook):
        _, user = authenticate()
        response = update_notebook(user=user)
        assert response.status_code == status.HTTP_200_OK

    def test_update_notebook_if_user_is_authenticated_and_has_perm_return_403(self, authenticate, update_notebook):
        _, user = authenticate()
        response = update_notebook(user_prem=user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_notebook_if_user_is_not_authenticated_return_401(self, update_notebook):
        response = update_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_notebook_if_user_is_not_owner_and_not_perm_return_404(self, authenticate, update_notebook):
        authenticate()
        response = update_notebook()
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestAssignPermNoteBook:
    def test_assign_perm_notebook_if_user_is_authenticated_and_owner_return_201(self, authenticate,
                                                                                assign_perm_notebook):
        _, user = authenticate()
        response = assign_perm_notebook(user=user)
        assert response.status_code == status.HTTP_201_CREATED

    def test_assign_perm_notebook_if_user_is_authenticated_and_has_perm_return_403(self, authenticate,
                                                                                   assign_perm_notebook):
        _, user = authenticate()
        response = assign_perm_notebook(user_perm=user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_assign_perm_notebook_if_user_is_not_authenticated_return_401(self, assign_perm_notebook):
        response = assign_perm_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_assign_perm_notebook_if_user_is_not_owner_and_not_perm_return_404(self, authenticate,
                                                                               assign_perm_notebook):
        authenticate()
        response = assign_perm_notebook()
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestRemovePermNoteBook:
    def test_remove_perm_notebook_if_user_is_authenticated_and_owner_return_201(self, authenticate,
                                                                                remove_perm_notebook):
        _, user = authenticate()
        response = remove_perm_notebook(user=user)
        assert response.status_code == status.HTTP_201_CREATED

    def test_remove_perm_notebook_if_user_is_authenticated_and_has_perm_return_403(self, authenticate,
                                                                                   remove_perm_notebook):
        _, user = authenticate()
        response = remove_perm_notebook(user_perm=user)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_remove_perm_notebook_if_user_is_not_authenticated_return_401(self, remove_perm_notebook):
        response = remove_perm_notebook()
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_remove_perm_notebook_if_user_is_not_owner_and_not_perm_return_404(self, authenticate,
                                                                               remove_perm_notebook):
        authenticate()
        response = remove_perm_notebook()
        assert response.status_code == status.HTTP_404_NOT_FOUND
