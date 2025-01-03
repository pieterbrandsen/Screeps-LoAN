import click
from screeps_loan import app
from screeps_loan.screeps_client import get_client

import screeps_loan.models.alliances as alliances
import screeps_loan.models.users as users_model

import json
import requests


alliance_segment = 99
clone_segment = 98


@app.cli.command()
def export_to_segments():
    click.echo("Exporting Alliance and Bot Data To Segment")

    r = requests.get("http://localhost:5000/vk/bots/league.json")
    if r.status_code == requests.codes.ok:
        clone_data = r.text
    else:
        clone_data = False

    alliance_query = alliances.AllianceQuery()
    all_alliances = alliance_query.getAll()

    alliances_id = [item["id"] for item in all_alliances]
    users_with_alliance = users_model.UserQuery().find_name_by_alliances(alliances_id)

    alliances_aux = {}
    for alliance in all_alliances:
        members = [
            user["name"]
            for user in users_with_alliance
            if user["alliance_id"] == alliance["id"]
        ]
        if len(members) < 2:
            continue
        alliances_aux[alliance["fullname"]] = members

    alliance_json = json.dumps(alliances_aux)

    screeps = get_client()
    shards = screeps.get_shards()
    for shard in shards:
        screeps.set_segment(alliance_segment, alliance_json, shard)
        if clone_data:
            screeps.set_segment(clone_segment, clone_data, shard)
