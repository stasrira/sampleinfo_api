"""OpenAPI v3 Specification"""

# apispec via OpenAPI
from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from marshmallow import Schema, fields

# Create an APISpec
spec = APISpec(
    title="SampleInfo API",
    version="1.0",
    openapi_version="3.0.2",
    plugins=[FlaskPlugin(), MarshmallowPlugin()],
)

# Define schemas
# class MetadataSchema1(Schema):
#     study_id = fields.Int(description="An integer value corresponds to the study_id that can be found in the metadata_stats output", required=True)

class OutputSchema(Schema):
    data = fields.String(description="Dataset output from the database. Always present if not errors were produced.")
    status = fields.Int(description="Status of the api call.", required=True)
    message = fields.String(description="Provides details of the error if api call has failed")

# register schemas with spec
# spec.components.schema("Input", schema=InputSchema)
spec.components.schema("Output", schema=OutputSchema)

# add swagger tags that are used for endpoint annotation
# tags = [
#             {'name': 'statistic info',
#              'description': 'Retrieves statistic information about data stored in the DB.'
#             },
#             {'name': 'metadata',
#              'description': 'Retrieves Metadata dataset.'
#             },
#        ]
#
# for tag in tags:
#     print(f"Adding tag: {tag['name']}")
#     spec.tag(tag)