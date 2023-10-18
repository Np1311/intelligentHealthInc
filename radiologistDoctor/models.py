from django.db import models

# Create your models here.
class findingsTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    template_name = models.CharField(max_length=255)
    template = models.TextField()

    @classmethod
    def viewTemplate(cls):
        templates = cls.objects.all()
        return templates
    
    @classmethod
    def deleteTemplateById(cls, template_id):
        try:
            template_to_delete = cls.objects.get(id=template_id)
            template_to_delete.delete()
            return True, "Template deleted successfully."
        except cls.DoesNotExist:
            return False, "Template with the given ID does not exist."