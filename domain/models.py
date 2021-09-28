from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Domain(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)


class Skill(models.Model):
    code = models.IntegerField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)


class Strategy(models.Model):
    code = models.IntegerField()
    skill_goal = models.ForeignKey(Skill, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    problem_formulation = models.TextField(null=True, blank=True)


class Action(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField()
    prerequisites = models.ManyToManyField(Strategy, through='Prerequisite', related_name='prerequisites')


class Prerequisite(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)


@receiver(post_save, sender=Domain)
def set_plugs_in_domain(sender, instance, created, **kwargs):
    if created:
        Skill.objects.create(domain=instance,
                             code=0,
                             name="Заглушка")


@receiver(post_save, sender=Skill)
def set_plugs_in_domain(sender, instance, created, **kwargs):
    if created:
        instance.code = max(Skill.objects.filter(domain=instance.domain).values_list('code', flat=True)) + 1
        instance.save()


@receiver(post_save, sender=Action)
def set_plugs_in_domain(sender, instance, created, **kwargs):
    if created:
        instance.order = max(Action.objects.filter(strategy=instance.strategy).values_list('order', flat=True), default=0) + 1
        instance.save()
