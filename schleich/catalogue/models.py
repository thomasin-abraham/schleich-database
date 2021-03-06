import re
import os
from django.db import models
from schleich.settings import MEDIA_ROOT
from django.template import defaultfilters
from tagging.models import Tag

STATUS_CHOICES = (
    (u'Extinct', u'Extinct'),
    (u'Extinct in the Wild', u'Extinct in the Wild'),
    (u'Critically Endangered', u'Critically Endangered'),
    (u'Endangered', u'Endangered'),
    (u'Vulnerable', u'Vulnerable'),
    (u'Near Threatened', u'Near Threatened'),
    (u'Least Concern', u'Least Concern'),
    (u'Common', u'Common')
)

GENDER_CHOICES = (
    (u'M', u'Male'),
    (u'F', u'Female'),
    (u'NA', u'Not applicable')
)

RELATIONSHIP_CHOICES = (
    (u'Mother', u'Mother'),
    (u'Father', u'Father'),
    (u'Daughter', u'Daughter'),
    (u'Son', u'Son'),
    (u'Twin', u'Twin'),
    (u'Sister', u'Sister'),
    (u'Brother', u'Brother'),
    (u'Mate', u'Mate'),
)

CONTINENT_CHOICES = (
    (u'Africa', u'Africa'),
    (u'Asia', u'Asia'),
    (u'Australia', u'Australia'),
    (u'Poles', u'Poles'),
    (u'Europe', u'Europe'),
    (u'America', u'America'),
    (u'Ocean', u'Ocean'),
    (u'Domestic', u'Domestic')
)

CAT_CHOICES = (
    (u'Person', u'Person'),
    (u'Vehicles', u'Vehicles'),
    (u'Buildings', u'Buildings'),
    (u'Accessories', u'Accessories'),
    (u'Foliage', u'Foliage')
)

AGE_CHOICES = (
    (u'Adult', u'Adult'),
    (u'Youth', u'Youth')
)

class Species(models.Model):
    species_name = models.CharField(max_length=100, help_text="If there are no sub-species, write the species name in the sub-species box", blank=True)
    subspecies_name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES)
    global_home = models.CharField(max_length=30, choices=CONTINENT_CHOICES)
    primary_habitat = models.CharField(max_length=100, help_text="Leave blank if animal is domestic", blank=True)
    def __unicode__(self):
        return self.subspecies_name

def image_file(instance, filename):
    base = "images/animals/%s"%defaultfilters.slugify(instance.name)
    ext = os.path.splitext(filename)[1]
    base = base + ext
    return base

def get_hashes(text):
    return re.findall('#[\w-]+', text)

class Animal(models.Model):
    species = models.ForeignKey(Species, related_name = 'Animal')
    image = models.ImageField(upload_to=image_file, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    age = models.CharField(max_length=30, choices=AGE_CHOICES)
    weight = models.IntegerField(help_text="Calculated in grams, don't put the 'g' at the end of the number")
    height = models.DecimalField(decimal_places=1, max_digits=100, help_text="Calculated in centimetres, to one decimal place.<br />From the floor to the highest point on the animal.")
    posture = models.CharField(max_length=500, help_text="Left/right is worked out by looking at the animal from <i><b>behind</b></i>")
    special_markings = models.CharField(max_length=100, help_text="Only if it distinguishes it from other animals from the same product line", blank=True)
    personality = models.TextField(max_length=5000, help_text="Please write as much as possible")
    other_information = models.TextField(max_length=5000, help_text="Please write as much as possible")
    catalogue_number = models.IntegerField()
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    year_made = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/catalogue/%s"%(self.slug,)   

class Relationship(models.Model):
    image = models.ImageField(upload_to="images/animals/relationships/", null=True, blank=True)
    information = models.TextField(max_length=5000, help_text="Notes on their relationship", blank=True)
    first_animal = models.ForeignKey(Animal, related_name="first_relationship")
    second_animal = models.ForeignKey(Animal, related_name = "second_relationship")
    relationship = models.CharField(max_length=30, choices=RELATIONSHIP_CHOICES, help_text="First animal is the<br />X of the second animal")
    def __unicode__(self):
        return '%s is the %s of %s' % (self.first_animal, self.relationship, self.second_animal)

class Story(models.Model):
    title = models.CharField(max_length=30, unique=True)
    desc = models.CharField(max_length=50, blank=True, help_text="A short description to help you identify the story, must be less than fifty letters long.")
    slug = models.SlugField(max_length=30, unique=True, null=True, blank=True)
    story = models.TextField(help_text='Put a # before character names, and if using html tags you <i>must</i> remember to close them.')
    
    def save(self, *args, **kwargs):
        super(Story, self).save(*args, **kwargs)
        hashes = get_hashes(self.story)
        tags = [tag.name for tag in Tag.objects.get_for_object(self) if tag.name not in hashes]
        tags.append(hashes)
        Tag.objects.update_tags(self, ','.join(hashes))
        animals = Animal.objects.all()
        names = dict([(a.name, a) for a in animals])
        names.update(dict([(a.slug, a) for a in animals]))
        for h in hashes:
            name = h.split('#')[1]
            if name in names.keys():
                Tag.objects.add_tag(names[name], 'story:%s'%self.slug)

    def get_absolute_url(self):
        return "/stories/%s"%(self.slug,)   

class Other(models.Model):
    name = models.CharField(max_length=30, help_text="Only if applicable", blank=True)
    image = models.ImageField(upload_to="images/animals/", null=True, blank=True)
    model_type = models.CharField(max_length=30)
    global_home = models.CharField(max_length=30, choices=CONTINENT_CHOICES, help_text="Only if applicable", blank=True)
    scientific_name = models.CharField(max_length=100, help_text="Only if applicable", blank=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, help_text="Only if applicable", blank=True)
    catalogue_number = models.IntegerField()
    year_made = models.IntegerField()
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES)
    weight = models.IntegerField(help_text="In grams, please")
    height = models.DecimalField(decimal_places=1, max_digits=100, help_text="Calculated in centimetres, to one decimal place. <br /> From the floor to the highest point.")
    category = models.CharField(max_length=30, choices=CAT_CHOICES)
    def __unicode__(self):
        return self.model_type



