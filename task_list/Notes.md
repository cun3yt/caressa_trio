These are deleted from `models.py` and may come back again in the future.

```python
class Caretaker(models.Model):
    class Meta:
        db_table = 'caretaker'

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

    FEMALE = 'FEMALE'
    MALE = 'MALE'

    GENDER_SET = (
        (FEMALE, 'Female'),
        (MALE, 'Male'),
    )

    gender = models.TextField(
        choices=GENDER_SET,
        default=FEMALE,
    )

    birth_date = models.DateField()

    extra_data = JSONField()
    circle = models.ManyToManyField(
        User,
        through='CaretakerCircleMembership',
        through_fields=('caretaker', 'circle_member'),
        related_name="circle_member_of",
    )

    def __str__(self):
        return "{} ({})".format(self.user.username, self.user.get_full_name())


class CaretakerCircleMembership(TimeStampedModel):
    class Meta:
        db_table = 'caretaker_circle_membership'

    caretaker = models.ForeignKey(Caretaker, on_delete=models.CASCADE)
    circle_member = models.ForeignKey(User, on_delete=models.CASCADE)

    # member's relationship to the caretaker
    relation_to_caretaker = models.TextField(null=True, default=None)


class CaretakerTask(TimeStampedModel):
    class Meta:
        db_table = 'caretaker_task'

    caretaker = models.ForeignKey(Caretaker, on_delete=models.CASCADE, related_name="tasks")
    title = models.TextField()
    details = models.TextField()
    ideal_time_to_do = models.DateTimeField()
    done_time = models.DateTimeField(null=True, default=None, blank=True)

    # TODO: assurance of being in circle?
    assigned_to = models.ForeignKey(User, null=True, default=None, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{id}: {title}".format(id=self.id, title=self.title)
```
