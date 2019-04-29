from django.db import models

class Policy(models.Model):
    name = models.CharField(max_length=100)
    detail = models.TextField(blank=True)
    
    class Meta:
        # db_table = 'policy'
        ordering = ['name']
        verbose_name_plural = 'policies'

    def __str__(self):
        return self.name
        
class Section(models.Model):
    policy = models.ForeignKey(
        Policy, on_delete=models.CASCADE, null=True,
        related_name='sections')
    name = models.CharField(max_length=100)
    detail = models.TextField()
    
    class Meta:
        # db_table = 'section'
        ordering = ['name']
        
    def __str__(self):
        return self.name