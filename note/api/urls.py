from rest_framework.routers import DefaultRouter

from note.api.api_views import NoteBookViewSet, NoteViewSet, BookMarkViewSet, CommentViewSet

app_name = 'note'

router = DefaultRouter()
router.register(r'notebooks', NoteBookViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'bookmarks', BookMarkViewSet)
router.register(r'comments', CommentViewSet)
urlpatterns = router.urls
