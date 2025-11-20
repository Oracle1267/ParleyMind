from backend.main import app
from backend.models import db, NCAABTeam, TeamDossier

with app.app_context():
    duke = NCAABTeam.query.filter_by(name='Duke Blue Devils').first()
    if duke:
        print(f'Duke found: ID={duke.id}, ESPN_ID={duke.espn_id}')
        dossier = TeamDossier.query.filter_by(team_id=duke.id).order_by(TeamDossier.snapshot_date.desc()).first()
        if dossier:
            print(f'Dossier: {dossier.wins}-{dossier.losses}, injuries={dossier.active_injuries}')
        else:
            print('No dossier found')
    else:
        print('Duke not found, checking available teams:')
        teams = NCAABTeam.query.limit(10).all()
        for t in teams:
            print(f'  - {t.name}')
