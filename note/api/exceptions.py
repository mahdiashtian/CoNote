from rest_framework.exceptions import APIException


class PasswordDoesNotMatch(APIException):
    status_code = 400
    default_detail = 'پسورد ها با یک دیگر تطابق ندارند.'
    default_code = 'password_does_not_match'


class NoteBookIsRequired(APIException):
    status_code = 400
    default_detail = 'notebook is required'
    default_code = 'notebook_is_required'
