from .forms import RecipeSearchForm


def search_form(request):
    # Add the RecipeSearchForm to the context
    return {"search_form": RecipeSearchForm()}
