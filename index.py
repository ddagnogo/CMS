# coding: utf8
from flask import Flask
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from flask import Response
from flask import g
from database import Database
from flask import url_for
from utilitaire import Utilitaire
import hashlib
import uuid
from functools import wraps
from flask import jsonify


app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not is_authenticated(session):
            return send_unauthorized()
        return f(*args, **kwargs)
    return decorated


@app.route('/')
def page_demarrage():
    utilisateur = None
    articles = get_db().get_articles()
    if "id" in session:
        return redirect('/admin')
    return render_template("form-accueil.html", articles=articles)


@app.route('/admin')
def recherche_complete():
    articles = get_db().search_all()
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
        return render_template('admin-accueil.html', articles=articles,
                utilisateur=utilisateur)
    return render_template("connectez-vous.html")


@app.route('/admin-nouveau')
@authentication_required
def activer_formulaire_admin_nouveau():
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    return render_template('form-admin-nouveau.html',
            utilisateur=utilisateur)


@app.route('/admin-nouveau/article', methods=['POST'])
def creer_nouvel_article():
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    titre = request.form['titre']
    identifiant = request.form['identifiant']
    auteur = request.form['auteur']
    jour = request.form['jour']
    mois = request.form['mois']
    annee = request.form['annee']
    paragraphe = request.form['paragraphe']
    article = [titre, identifiant, auteur, annee, paragraphe]
    taille = [len(titre), len(identifiant), len(auteur), len(annee),
            len(paragraphe)]
    if len(titre) == 0 or len(identifiant) == 0 or len(auteur) == 0 or len(jour) == 0 or len(mois) == 0 or len(annee) == 0 or len(paragraphe) == 0:
        return render_template('form-admin-nouveau.html', article=article,
                                taille=taille, utilisateur=utilisateur)
    elif Utilitaire.verifier_donnee_identifiant(identifiant):
        non_char = Utilitaire.verifier_donnee_identifiant(identifiant)
        return render_template('form-admin-nouveau.html', article=article,
                non_char=non_char, utilisateur=utilisateur)
    elif Utilitaire.verifier_donnee_date(annee, mois, jour):
        date = Utilitaire.verifier_donnee_date(annee, mois, jour)
        date_e = str('-'.join((jour, mois, annee)))
        return render_template('form-admin-nouveau.html', article=article,
                    date=date, date_e=date_e, utilisateur=utilisateur)
    else:
        date_e = str('-'.join((annee, mois, jour)))
        get_db().insert_article(titre, identifiant,
                                auteur, date_e, paragraphe)
        return redirect('/')


@app.route('/ajax/<suggestion>')
def valider_suggestion(suggestion):
    suggest = get_db().verify_suggestion(suggestion)
    if suggest is None:
        return render_template("identifiant.html", suggestion=suggestion)
    caract_final = suggestion[len(suggestion) - 1]
    if caract_final.isdigit():
        caract_final = int(caract_final) + 1
    else:
        caract_final = "1"
    suggestion = suggestion + caract_final
    return render_template("identifiant.html", suggestion=suggestion)


@app.route('/ajax/modification/<modif>')
def valider_modification(modif):
    modification = get_db().verify_suggestion(modif)
    return render_template("modification.html", modification=modification)


@app.route('/articles/')
def chercher():
    mots = request.args.get('recherche', '')
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    if(len(mots) > 0):
        results = get_db().search_words(mots)
        return render_template("resultat-recherche.html", results=results,
                                utilisateur=utilisateur)
    else:
        return render_template("resultat-recherche.html",
                                    utilisateur=utilisateur)


@app.route('/article/<identifier>')
def trouver_article(identifier):
    articles = get_db().search_article(identifier)
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    if len(articles) == 0:
        return render_template("404.html", utilisateur=tilisateur), 404
    else:
        return render_template("form-accueil.html", articles=articles,
                                                    utilisateur=utilisateur)


@app.route('/article/modification/<identifier>')
@authentication_required
def modifier_article(identifier):
    articles = get_db().search_article(identifier)
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    if articles is None or len(articles) == 0:
        return render_template("404.htlm", utilisateur=utilisateur), 404
    else:
        return render_template("form-modification.html",
                articles=articles, utilisateur=utilisateur)


@app.route('/article/update', methods=['POST'])
def mettre_a_jour():
    titre = request.form['titre']
    identifiant = request.form['identifiant']
    auteur = request.form['auteur']
    date_publication = request.form['date_publication']
    paragraphe = request.form['paragraphe']
    articles = {"titre": titre, "identifiant": identifiant, "auteur": auteur,
                "date_publication": date_publication, "paragraphe": paragraphe}
    modif = [titre, paragraphe]
    taille = [len(titre), len(paragraphe)]
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    if len(titre) == 0 or len(paragraphe) == 0:
        return render_template("form-modification.html", articles=articles,
                               modif=modif, taille=taille,
                               utilisateur=utilisateur)
    else:
        get_db().update(titre, paragraphe, identifiant)
        return redirect('/admin')


@app.route('/confirmation')
def confirmation_page():
    return render_template('confirmation.html')


@app.route('/formulaire', methods=["GET", "POST"])
def creer_user():
    if request.method == "GET":
        return render_template("user-creation.html",)
    else:
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        if username == "" or password == "" or email == "":
            return render_template("user-creation.html", error="Tous"
                                   "les champs sont requis")
        user_existant = get_db().get_user_login_info(username)
        if user_existant:
            return render_template("user-creation.html", error="Cet"
                                   "nom utilisateur existe deja")
        mail = get_user_login_info_email(email)
        if mail:
            return render_template("user-creation.html", error="Cet courriel"
                                   "existe deja")
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha512(password + salt).hexdigest()
        get_db().create_user(username, email,  salt, hashed_password)
        return redirect("/")


@app.route('/login', methods=["POST"])
def log_user():
    username = request.form["username"]
    password = request.form["password"]
    if username == "" or password == "":
        return redirect('/')
    user = get_db().get_user_login_info(username)
    if user is None:
        return render_template("non-connecte.html")
    salt = user[0]
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    if hashed_password == user[1]:
        id_session = uuid.uuid4().hex
        get_db().save_session(id_session, username)
        session["id"] = id_session
        return redirect('/')
    else:
        return render_template("non-connecte.html")


@app.route('/logout')
@authentication_required
def logout():
    if session.has_key("id"):
        id_session = session["id"]
        session.pop('id', None)
        get_db().delete_session(id_session)
    return redirect('/')


@app.route('/config')
def parameter():
    fichier = open("config.txt")
    donnee = fichier.read()
    fichier.close()
    donnee = donnee.split('\n')
    username = donnee[0]
    password = donnee[1]
    email = donnee[2]
    salt = uuid.uuid4().hex
    hashed_password = hashlib.sha512(password + salt).hexdigest()
    get_db().create_user(username, email, salt, hashed_password)
    return redirect("/")


@app.route('/api/articles/', methods=["GET", "POST"])
def get_public():
    if request.method == "GET":
        data = get_db().get_published()
        return jsonify(data)
    else:
        data = request.get_json()
        titre = data["titre"]
        identifiant = data["identifiant"]
        auteur = data["auteur"]
        date_publication = data["date_publication"]
        paragraphe = data["paragraphe"]
        existe = get_db().search_article(identifiant)
        if existe is None:
            get_db().insert_article(identifiant, titre,
                                    auteur, date_publication, paragraphe)
            return "", 201
        return "", 400


@app.route('/api/article/<identifier>', methods=["GET"])
def get_article_identifier(identifier):
    if request.method == "GET":
        data = get_db().search_article(identifier)
        if len(data) == 0:
            return "", 404
        return jsonify(data)


@app.route('/doc')
def get_api_documentation():
    utilisateur = None
    if "id" in session:
        utilisateur = get_db().get_session(session["id"])
    return render_template("doc.html", utilisateur=utilisateur)


def is_authenticated(session):
    return session.has_key("id")


def send_unauthorized():
    return Response('Vous devez vous connecter', 401)

app.secret_key = "(*&*&322387he738220)(*(*22347657"
