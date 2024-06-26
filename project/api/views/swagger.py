from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.views import SpectacularAPIView
from rest_framework.response import Response


class CustomSchemaGenerator(SchemaGenerator):
    def parse(self, request, public):
        # Custom logic to filter endpoints
        endpoints = super().parse(request, public)

        included_endpoints = [
            ("/get_profile/", "Profile"),
            ("/edit_profile/", "Profile"),
            ("/signup/", "Auth"),
            ("/login/", "Auth"),
            ("/logout/", "Auth"),
            ("/auth_check/", "Auth"),
            ("/send_password_reset_email/", "Auth"),
            ("/verify_password_reset_token/", "Auth"),
            ("/set_new_password/", "Auth"),
            ("/activate_account/<uidb64>/<token>/", "Auth"),

        ]

        filtered_endpoints = {}
        for endpoint, new_tag in included_endpoints:
            filtered_endpoints[endpoint] = endpoints[endpoint]
            if new_tag:
                for method, attributes in filtered_endpoints[endpoint].items():
                    attributes["tags"] = [new_tag]

        return filtered_endpoints


class SpectacularSwagger(SpectacularAPIView):
    generator_class = CustomSchemaGenerator

    def _get_schema_response(self, request):
        # Use the custom generator class
        generator = self.generator_class(
            urlconf=self.urlconf, api_version=self.api_version, patterns=self.patterns
        )
        return Response(
            data=generator.get_schema(request=request, public=self.serve_public),
            headers={
                "Content-Disposition": f'inline; filename="{self._get_filename(request, self.api_version)}"'
            },
        )
