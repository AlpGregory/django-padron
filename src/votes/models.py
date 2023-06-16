from django.db import models


class Location(models.Model):
    """
    Model for vote locations in Costa Rica.

    ...

    Attributes
    ----------
    elec_code : CharField
        location's electoral code. This is the primary key.
    province : CharField
        name of the province.
    canton : CharField
        name of the canton
    district : CharField
        name of the district

    Methods
    -------
    """
    elec_code = models.CharField('electoral code', max_length=200, primary_key=True)
    province = models.CharField(max_length=200)
    canton = models.CharField(max_length=200)
    district = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.district}, {self.canton}, {self.province}"

    class Meta:
        indexes = [
            models.Index(fields=['province']),
            models.Index(fields=['canton']),
            models.Index(fields=['district']),
        ]


class Person(models.Model):
    """
    Model for Costa Rican voters.

    ...

    Attributes
    ----------
    identification : CharField
        legal identification in Costa Rica
    elec_code : CharField
        foreign key of location model
    voting_board : CharField
        voting board within the vote location
    full_name : CharField
        person's full name
    gender : CharField
        person's gender. the person is a man if id's fourth digit is even, otherwise is a woman.

    Methods
    -------
    """
    identification = models.CharField(max_length=15, primary_key=True)
    elec_code = models.ForeignKey(Location, on_delete=models.CASCADE)
    voting_board = models.CharField(max_length=15)
    full_name = models.CharField('name', max_length=200)
    gender = models.CharField(max_length=200)
    id_expiration_date = models.DateField()

    def __str__(self):
        return f"Cedula: {self.identification}, {self.full_name}"

    class Meta:
        indexes = [
            models.Index(fields=['identification', 'elec_code', 'gender']),
            models.Index(fields=['identification', 'id_expiration_date']),
        ]
