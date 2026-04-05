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

"""
Module de gestion du hachage des mots de passe.
"""

import hashlib
import uuid


def generate_mot_de_passe_hash(mot_de_passe):
    salt = uuid.uuid4().hex
    mot_de_passe_hash = hashlib.sha512(
        str(mot_de_passe + salt).encode("utf-8")
    ).hexdigest()
    return salt, mot_de_passe_hash


def derive_mot_de_passe_hash(salt, mot_de_passe):
    return hashlib.sha512(str(mot_de_passe + salt).encode("utf-8")).hexdigest()
