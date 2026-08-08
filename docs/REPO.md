# REPO.md

cricket-app/
├── backend/                  # Django Backend (DRF)
│   ├── core/                 # Django settings, wsgi, urls
│   ├── matches/              # Models, serializers, API views
│   │   ├── [models.py](http://models.py/)         # (Team, Player, Match, Innings, BallEvent)
│   │   ├── [views.py](http://views.py/)          # API endpoints for scoring & live match
│   │   └── [urls.py](http://urls.py/)
│   ├── requirements.txt      # Python dependencies (django, djangorestframework, etc.)
│   └── [manage.py](http://manage.py/)
├── frontend/                 # Vue.js Frontend (Vite)
│   ├── src/
│   │   ├── views/            # Setup.vue, ScorerDashboard.vue, ViewerLive.vue, History.vue
│   │   ├── components/       # Reusable UI parts (ScoreCard, WicketModal, etc.)
│   │   └── App.vue
│   ├── package.json          # Node dependencies
│   └── vite.config.js
├── Dockerfile                # Packages Python, Node build steps, and SQLite
└── docker-compose.yml        # Orchestrates the local container