from django.db import models

class AuthorizedUser(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email


class SiteSettings(models.Model):
    """Singleton-like site-wide settings stored in the DB.

    Holds configurable branding and theme values to avoid local file storage.
    """
    theme_color = models.CharField(max_length=7, default="#e74c3c")
    logo_url = models.CharField(max_length=512, default="/static/images/EagleForceLogo.png")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"SiteSettings(color={self.theme_color})"