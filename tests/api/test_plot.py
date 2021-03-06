from flask import url_for
from plotly.offline import plot
import json

from megaqc.rest_api.schemas import TrendSchema
from marshmallow.utils import EXCLUDE

from tests import factories


def test_get_trend_series(db, client):
    # Create 5 reports each with 1 sample. Each has a single field called 'test_field'
    data_type = factories.SampleDataTypeFactory()
    report = factories.ReportFactory.create_batch(5, samples__data__data_type=data_type)
    db.session.add_all(report)
    db.session.commit()

    # plots = jpi.get('plots/trends/series')
    url = url_for(
        'rest_api.trend_data',
        filter=json.dumps([]),
        fields=json.dumps([data_type.data_key])
    )
    response = client.get(url, headers={'Content-Type': 'application/json'})

    # Check the request was successful
    assert response.status_code == 200, response.json

    # unknown=EXCLUDE ensures we don't keep the ID field when we load at this point
    data = TrendSchema(many=True, unknown=EXCLUDE).load(response.json)

    # Check that there are 4 series (mean, stdev, raw data, outliers)
    assert len(data) == 4

    # Test that this is valid plot data
    plot({'data': data}, validate=True, auto_open=False)
