from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


class Domain(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "[%d] %s" % (self.code, self.name)


class Skill(models.Model):
    code = models.IntegerField()
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return "[%d] %s" % (self.code, self.name)


class Strategy(models.Model):
    code = models.IntegerField()
    skill_goal = models.ForeignKey(Skill, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    problem = models.TextField(null=True, blank=True)

    def __str__(self):
        return "[%d] %s" % (self.code, self.name)


class Action(models.Model):
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)
    order = models.IntegerField()
    description = models.TextField()
    prerequisites = models.ManyToManyField(Strategy, through='Prerequisite', related_name='prerequisites')


class Prerequisite(models.Model):
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    strategy = models.ForeignKey(Strategy, on_delete=models.CASCADE)


@receiver(pre_save, sender=Domain)
def set_domain_code(sender, instance, **kwargs):
    if instance.pk is None:
        instance.code = max(Domain.objects.all().values_list('code', flat=True), default=0) + 1


@receiver(post_save, sender=Domain)
def set_plugs_in_domain(sender, instance, created, **kwargs):
    if created:
        Skill.objects.create(domain=instance,
                             code=0,
                             name="Заглушка")


@receiver(pre_save, sender=Skill)
def set_skill_code(sender, instance, **kwargs):
    if instance.pk is None:
        instance.code = max(Skill.objects.filter(domain=instance.domain).values_list('code', flat=True), default=0) + 1


@receiver(pre_save, sender=Strategy)
def set_strategy_code(sender, instance, **kwargs):
    if instance.pk is None:
        instance.code = max(Strategy.objects.filter(skill_goal=instance.skill_goal).values_list('code', flat=True),
                            default=0) + 1


@receiver(pre_save, sender=Action)
def set_action_order(sender, instance, **kwargs):
    if instance.pk is None:
        instance.order = max(Action.objects.filter(strategy=instance.strategy).values_list('order', flat=True),
                             default=0) + 1
