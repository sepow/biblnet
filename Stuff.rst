
bruger: http://sphinx.pocoo.org/rest.html

======
Tribes
======

indeholder 

tribe
-----

* En tribe kan være enten privat, eller public. 

* Hvis en tribe er public kan *alle* læse *alt* indholdet.
* Alle autorisrede users kan blive medlemmer.

Medlemmer kan...
^^^^^^^^^^^^^^^^
* Alle medlemmer af en Tribe kan oprette indhold (topic, comment, dokument, wikiside, tag).

Creator kan.. 
^^^^^^^^^^^^^

* En Tribes creator er automatisk med i 'moderators' for den oprettede tribe. 
* En Tribes creator kan gøre en tribe privat, og omvendt. 
* En Tribes creator kan gøre andre medlemmer til moderators.
* En Tribes creator kan slette gruppen.
* En Tribes creator kan edite tråde og comments.
* En Tribes creator kan slette topics og tråde.
* En Tribes creator kan smide alle ud af gruppen.

Moderators kan..
^^^^^^^^^^^^^^^^
* Moderators kan gøre tråde sticky og lukke tråde.
* Moderators kan invitere medlemmer til gruppen. 
* Moderators kan smide almindelige medlemmer ud af gruppen

wiki
----

topic
-----

comments
-------

dms
---



Gør det muligt at edite topics

Skriv tests for tribe funktionallitet. 

Add knapper på tribe medlemmer listen, 'add to moderators' og 'kick from group'


Serveren:
    Opret cronjob med for emails

Ved syncdb:
    Opret en global fælles tribe "global"
    Opret affiliations


# Users joiner en affiliation tribe ved oprettelse. 
Administrators                       : admin ? private tribe
Danmarks Biblioteksskole - København : db-kbh
Danmarks Biblioteksskole - Aalborg   : db-aa
Universitetsansatte                  : uni
Syddansk Universitet                 : sdu
It-Universitetet                     : itu
Tidligere studerende                 : alumni
International Students               : inter
Biblioteksrelevante organisationer   : bib-org
Eksterne brugere                     : ext

En fælles gruppe for x. 


tags: sluggen, fælles

Eventurelt mulighed for at joine et stamhold samtidig?

python manage.py dumpdata > /home/sean/programming/pinax-env/biblnet/apps/sepow/fixtures/initial_data.json

