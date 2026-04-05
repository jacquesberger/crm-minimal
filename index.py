# Copyright (C) 2026  CODE3 Cooperative de solidarite
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
from flask import Flask, make_response, jsonify
from flask import abort
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import send_from_directory
from flask_json_schema import JsonSchema
from dotenv import load_dotenv
from db import get_db
from authentication import authentication_required
from admin_required import admin_required
from password_hashing import generate_mot_de_passe_hash
from schema import (
    self_mot_de_passe_schema,
    admin_set_mot_de_passe_schema,
    new_utilisateur_schema,
    edit_utilisateur_schema,
)

import uuid
import os

from utils import by_name
from validations import (
    is_valid_user_login_info,
    validate_entreprise,
    validate_interaction,
    validate_rappel,
    validation_nouvel_utilisateur,
)


def minimal_factory():
    load_dotenv()
    app = Flask(__name__, static_url_path="", static_folder="static")
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
    schema = JsonSchema(app)

    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, "_database", None)
        if db is not None:
            db.disconnect()

    @app.route("/tableau-de-bord")
    @authentication_required
    def landing_page():
        rappels = get_db().get_rappels_todo()
        return render_template("landing.html", rappels=rappels)

    @app.route("/entreprises")
    @authentication_required
    def entreprises_liste():
        all_entreprises = get_db().get_entreprises()
        all_entreprises.sort(key=by_name)
        return render_template("entreprises.html", entreprises=all_entreprises)

    @app.route("/nouvelle-entreprise", methods=["GET", "POST"])
    @authentication_required
    def entreprise_add():
        if request.method == "GET":
            return render_template("entreprise-edit.html")
        else:
            validation_result = validate_entreprise(request.form)
            if validation_result["is_valid"]:
                last_id = get_db().add_entreprise(request.form["nom"])
                return redirect("/entreprise/" + str(last_id))
            else:
                return render_template("entreprise-edit.html", result=validation_result)

    @app.route("/entreprise/<id>")
    @authentication_required
    def entreprise_display(id):
        entreprise = get_db().get_entreprise(id)
        if entreprise is None:
            all_entreprises = get_db().get_entreprises()
            all_entreprises.sort(key=by_name)
            erreur = {"id": id, "code": 404}
            return render_template(
                "entreprises.html", entreprises=all_entreprises, erreur=erreur
            )
        else:
            interactions = get_db().get_interactions(entreprise["id"])
            rappels = get_db().get_rappels_non_termines(entreprise["id"])
            return render_template(
                "entreprise-display.html",
                entreprise=entreprise,
                interactions=interactions,
                rappels=rappels,
            )

    @app.route(
        "/entreprise/<entreprise_id>/nouvelle-interaction", methods=["GET", "POST"]
    )
    @authentication_required
    def interaction_add(entreprise_id):
        entreprise = get_db().get_entreprise(entreprise_id)
        if entreprise is None:
            abort(404)
        else:
            if request.method == "GET":
                return render_template("interaction-edit.html", entreprise=entreprise)
            else:
                validation_result = validate_interaction(request.form, entreprise["id"])
                if validation_result["is_valid"]:
                    id_session = session["id"]
                    utilisateur = get_db().get_utilisateur_info_by_session(id_session)
                    get_db().add_interaction(
                        datetime.date.fromisoformat(request.form["moment"]),
                        request.form["description"],
                        entreprise["id"],
                        utilisateur["username"],
                    )
                    return redirect("/entreprise/" + str(entreprise["id"]))
                else:
                    return render_template(
                        "interaction-edit.html",
                        entreprise=entreprise,
                        result=validation_result,
                    )

    @app.route("/entreprise/<entreprise_id>/nouveau-rappel", methods=["GET", "POST"])
    @authentication_required
    def rappel_add(entreprise_id):
        entreprise = get_db().get_entreprise(entreprise_id)
        if entreprise is None:
            abort(404)
        else:
            if request.method == "GET":
                return render_template("rappel-edit.html", entreprise=entreprise)
            else:
                validation_result = validate_rappel(request.form, entreprise["id"])
                if validation_result["is_valid"]:
                    get_db().add_rappel(
                        datetime.date.fromisoformat(request.form["activation"]),
                        request.form["note"],
                        entreprise["id"],
                    )
                    return redirect("/entreprise/" + str(entreprise["id"]))
                else:
                    return render_template(
                        "rappel-edit.html",
                        entreprise=entreprise,
                        result=validation_result,
                    )

    @app.route("/rappel/<rappel_id>")
    @authentication_required
    def retirer_rappel(rappel_id):
        get_db().delete_rappel(rappel_id)
        entreprise_id = request.args.get("entreprise")
        if entreprise_id is None:
            return redirect("/tableau-de-bord")
        else:
            return redirect("/entreprise/" + entreprise_id)

    @app.route("/rapports")
    @authentication_required
    def page_rapports():
        return render_template("rapports.html")

    @app.route("/resume-quotidien")
    @authentication_required
    def resume_quotidien():
        date = request.args.get("date")
        if date == "":
            return render_template(
                "rapports/resume-quotidien.html",
                erreur="Aucune date n'a été sélectionnée",
                date=date,
            )
        else:
            elements = get_db().get_resume_quotidien(date)
            return render_template(
                "rapports/resume-quotidien.html", date=date, elements=elements
            )

    @app.route("/resume-depuis")
    @authentication_required
    def resume_depuis_une_date():
        date = request.args.get("date")
        if date == "":
            return render_template(
                "rapports/resume-depuis.html",
                erreur="Aucune date n'a été sélectionnée",
                date=date,
            )
        else:
            elements = get_db().get_resume_depuis(date)
            return render_template(
                "rapports/resume-depuis.html", date=date, elements=elements
            )

    @app.route("/")
    @app.route("/login", methods=["GET", "POST"])
    def login_user():
        if request.method == "GET":
            return render_template("login.html")
        else:
            username = request.form["username"]
            password = request.form["password"]

            if username == "" or password == "":
                abort(400)
            try:
                user_login_info = get_db().get_utilisateur_login_info(username)
                if user_login_info is None:
                    return (
                        render_template(
                            "login.html", error_request="Utilisateur non trouvé."
                        ),
                        404,
                    )

                if is_valid_user_login_info(user_login_info, password):
                    id_session = uuid.uuid4().hex
                    session["id"] = id_session
                    get_db().save_session(id_session, username)

                    session["id"] = id_session
                    session["role_id"] = get_db().get_role_id(username)
                    return redirect("/tableau-de-bord")
                else:
                    return (
                        render_template(
                            "login.html", error_request="Utilisateur non trouvé."
                        ),
                        404,
                    )
            except Exception as e:
                print(e)
                return (
                    render_template(
                        "login.html",
                        error_server="Une erreur est survenue " "côté serveur.",
                    ),
                    500,
                )

    @app.route("/logout")
    @authentication_required
    def logout():
        id_session = session.get("id")
        get_db().delete_session(id_session)
        session.clear()
        return redirect("/login")

    @app.route("/parametres/compte")
    @authentication_required
    def compte():
        id_session = session["id"]
        try:
            user = get_db().get_utilisateur_info_by_session(id_session)
            html_content = render_template("parametres/compte.html", utilisateur=user)
            if request.args.get("fragment"):
                return html_content

            else:
                return render_template(
                    "parametres/parametres.html", section=html_content
                )
        except Exception as e:
            print(e)
            return render_template("500.html"), 500

    @app.route("/parametres/utilisateurs")
    @admin_required
    def utilisateurs():
        try:
            user = get_db().get_utilisateur_info_by_session(session["id"])
            users = get_db().get_utilisateurs()
            roles = get_db().get_roles()
            html_content = render_template(
                "parametres/liste_utilisateurs.html",
                utilisateur=user,
                utilisateurs=users,
                roles=roles,
            )
            if request.args.get("fragment"):
                return html_content
            else:
                return render_template(
                    "parametres/parametres.html", section=html_content
                )
        except Exception as e:
            print(e)
            return render_template("500.html"), 500

    @app.route("/parametres/utilisateur/<user_id>")
    @admin_required
    def utilisateur(user_id):
        try:
            user = get_db().get_utilisateur_by_id(user_id)
            if not user:
                return render_template("404.html", erreur="Page non trouvée."), 404
            html_content = render_template(
                "parametres/utilisateur.html", utilisateur=user
            )
            if request.args.get("fragment"):
                return html_content
            else:
                return render_template(
                    "parametres/parametres.html", section=html_content
                )
        except Exception as e:
            print(e)
            return render_template("500.html"), 500

    ## Routes services REST
    @app.route("/api/doc")
    def api_docs():
        return send_from_directory("docs", "doc.html")

    @app.route("/api/utilisateurs", methods=["GET"])
    @authentication_required
    def get_utilisateurs():
        try:
            users = get_db().get_utilisateurs()
            return jsonify(users)

        except Exception as e:
            print(e)
            return jsonify({"Error": " Une erreur est survenue " "côté serveur."}), 500

    @app.route("/api/utilisateur", methods=["POST"])
    @authentication_required
    @schema.validate(new_utilisateur_schema)
    def creer_utilisateur():
        try:
            data = request.json
            validation = validation_nouvel_utilisateur(data)
            if validation["is_valid"]:
                user = get_db().get_utilisateur_login_info(data.get("nom-utilisateur"))
                if user:
                    return (
                        jsonify(
                            {
                                "Error": "Le nom d'utilisateur est déjà utilisé par un "
                                "autre utilisateur."
                            }
                        ),
                        409,
                    )
                salt, hashed_password = generate_mot_de_passe_hash(
                    data.get("mot-de-passe")
                )
                user = get_db().add_utilisateur_actif(
                    data.get("nom-utilisateur"),
                    data.get("mot-de-passe"),
                    salt,
                    hashed_password,
                    data.get("role"),
                )
                return jsonify(user)
            else:
                return jsonify({"Error": validation}), 400
        except Exception as e:
            print(e)
            return jsonify({"Error": " Une erreur est survenue " "côté serveur."}), 500

    @app.route("/api/utilisateur/<user_id>", methods=["PUT"])
    @admin_required
    @schema.validate(edit_utilisateur_schema)
    def modifier_utilisateur(user_id):
        try:
            data = request.get_json()
            role_id = data.get("role")
            etat_id = data.get("etat")

            utilisateur = get_db().modify_utilisateur(
                user_id, int(role_id), int(etat_id)
            )

            if utilisateur:
                return jsonify(utilisateur)

            return (
                jsonify(
                    {"Error": "L'utilisateur n'a pas été trouvé.", "user_id": user_id}
                ),
                404,
            )

        except Exception as e:
            print(e)
            return jsonify({"Error": "Une erreur est survenue côté serveur."}, 500)

    @app.route("/api/utilisateur/<user_id>/mot-de-passe", methods=["PUT"])
    @admin_required
    @schema.validate(admin_set_mot_de_passe_schema)
    def admin_set_mot_de_passe(user_id):
        data = request.get_json()
        new_password = data.get("nouveau-mot-de-passe")
        try:
            salt, mot_de_passe_hash = generate_mot_de_passe_hash(new_password)

            if get_db().modify_mot_de_passe_by_id(user_id, salt, mot_de_passe_hash):
                return jsonify({"Success": "Le mot de passe a été modifié."})
            else:
                return jsonify({"Error": "Le mot de passe n'a pu être modifié"}), 500
        except Exception as e:
            print(e)
            return jsonify({"Error": " Une erreur est survenue " "côté serveur."}), 500

    @app.route("/api/utilisateur/moi/mot-de-passe", methods=["PUT"])
    @authentication_required
    @schema.validate(self_mot_de_passe_schema)
    def self_mot_de_passe():
        id_session = session["id"]
        data = request.get_json()
        old_password = data.get("ancien-mot-de-passe")
        new_password = data.get("nouveau-mot-de-passe")

        if old_password == new_password:
            return (
                jsonify(
                    {
                        "Error": "Le nouveau mot de passe doit être différent de l'ancien."
                    }
                ),
                409,
            )

        try:
            utilisateur = get_db().get_utilisateur_info_by_session(id_session)
            user = get_db().get_utilisateur_login_info(utilisateur["username"])
            if not is_valid_user_login_info(user, old_password):
                return jsonify({"Error": "L'ancien mot de passe est invalide."}), 400
            salt, mot_de_passe_hash = generate_mot_de_passe_hash(new_password)
            if get_db().modify_mot_de_passe(
                utilisateur["username"], salt, mot_de_passe_hash
            ):
                return jsonify({"Success": "Le mot de passe a été modifié."}), 200
            else:
                return jsonify({"Error": "Le mot de passe n'a pu être modifié"}), 500

        except Exception as e:
            print(e)
            return jsonify({"Error": " Une erreur est survenue " "côté serveur."}), 500

    return app


if __name__ == "__main__":
    app = minimal_factory()
    app.run(debug=True)
