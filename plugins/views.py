from django import forms, template
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from feed.models import ConfiguredPlugin

from .models import Plugin, PluginVersion

STARTER_CODE = '''
/**
 * Returns true if the provided config is valid for this plugin version
 * @param {Object} config The configuration being validated
 * @returns {boolean} True if the config is valid, false if it is not
 */
function validateConfig(config) {
  /**
   * Check that the config has the required structure and fields
   */

  return true;
}

/**
 * @callback configCallback
 * @param {Object} configData The configuration data that should be stored and
 *                              passed to the fetchPosts function
 */

/**
 * An optional function that returns an HTML node that can be displayed in a
 *   modal for configuring and authenticating the plugin
 * @param {configCallback} callback The function that should be called when
 *                           the configuration is complete
 * @param {Object} previousConfig The preexisting configuration, or undefined
 *                                  if the plugin has not been configured yet,
 *                                  can possibly be a config generated by an
 *                                  older version of the plugin
 * @returns {Element} The HTML element that will be displayed in the modal
 */
function getConfigModal(callback, previousConfig) {
  /**
   * Construct an HTML element that will allow users to fill in configuration
   * information for the plugin, and will then pass that information to the
   * callback as a JSON object when the user is done with the configuration.
   */
}

/**
 * @callback postsCallback
 * @param{PostPage} The current page of posts, along with the pagination data
 *                    required to get the next page, or no paginationData if
 *                    there are no more pages of posts to retrieve
 */

/**
 * @typedef {object} Post
 * @property {string} title The title of the post - required
 * @property {string} author The author of the post - optional
 * @property {Date} date The date and time the post was created on - required
 * @property {string} link The URL the post should link to - optional
 * @property {string} content The HTML content of the post - optional
 * @property {string} comments The URL of the comments page - optional
 */

/**
 * @typedef {object} PostPage
 * @property {Post[]} posts The posts on this page
 * @property {object} paginationData An object that can be used to get the next
 *                                   page of posts - optional
 */

/**
 * Returns a page of posts that will be inserted into the main feed
 * @param {Object} configData Configuration JSON generated by the config modal
 * @param {Object} paginationData Pagination data returned in last request
 * @param {postsCallback} callback The function that should be called with the
 *                                   post page that was generated
 */
function fetchPosts(callback, configData, paginationData) {
  /**
   * Fetch the posts and pagination data, and put them in a PostPage object,
   * passing that object to the callback. An empty array of posts indicates
   * that there are no more pages of data to fetch.
   */
}
'''


class EditDescriptionForm(forms.ModelForm):
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'description',
        }), label='')

    class Meta:
        model = Plugin
        fields = [
            'description',
        ]


@login_required
@require_http_methods(["GET"])
def home(request):
    plugins = {}
    description_editors = {}
    owned_plugins = Plugin.objects.filter(owners=request.user.id)
    for plugin in owned_plugins:
        plugin_data = {}
        plugin_data['versions'] = plugin.pluginversion_set.all()
        plugin_data['edit_description'] = EditDescriptionForm(
            initial={'description': plugin.description})
        plugins[plugin] = plugin_data

    subscriptions = ConfiguredPlugin.objects.filter(user=request.user).all()

    return render(
        request, 'plugins/home.html', {
            'username': request.user.username,
            'plugins': plugins,
            'subscribed': [s.plugin_version.plugin for s in subscriptions],
            'subscribed_versions': [s.plugin_version for s in subscriptions],
            'description_editors': description_editors,
        })


class CreatePluginForm(forms.ModelForm):
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'name',
        }), label='')
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'placeholder': 'description',
        }), label='')

    class Meta:
        model = Plugin
        fields = [
            'name',
            'description',
        ]


def get_create_plugin(request):
    return render(request, 'plugins/create.html', {
        'form': CreatePluginForm(),
    })


def post_create_plugin(request):
    form = CreatePluginForm(request.POST)
    form.is_valid()
    if form.is_valid():
        plugin = form.save(commit=False)
        plugin.save()
        plugin.owners.add(request.user)
        plugin.save()
        return redirect('/plugins/update/' + str(plugin.id))

    return render(request, 'plugins/create.html', {
        'form': form,
    })


@login_required
@require_http_methods(["GET", "POST"])
def create_plugin(request):
    if request.method == "GET":
        return get_create_plugin(request)

    return post_create_plugin(request)


class AddOwnerForm(forms.Form):
    owner = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Owner',
        }), label='')


class RemoveOwnerForm(forms.Form):
    owner = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Owner',
        }), label='')


@login_required
@require_http_methods(["GET", "POST"])
def ownership(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)

    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.name,
            'plugin_owners': plugin.owners.all(),
        })

    return render(
        request, 'plugins/ownership.html', {
            'plugin': plugin,
            'add_owner_form': AddOwnerForm(),
            'remove_owner_form': RemoveOwnerForm(),
        })


@login_required
@require_http_methods(["POST"])
def add_ownership(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)

    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.name,
            'plugin_owners': plugin.owners.all(),
        })

    form = AddOwnerForm(request.POST)
    if form.is_valid():
        owner = form.cleaned_data['owner']
        user = get_object_or_404(User, username=owner)
        plugin.owners.add(user)

    return redirect('/plugins/ownership/' + str(plugin_id))


@login_required
@require_http_methods(["POST"])
def remove_ownership(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)

    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.name,
            'plugin_owners': plugin.owners.all(),
        })

    form = RemoveOwnerForm(request.POST)
    if form.is_valid():
        owner = form.cleaned_data['owner']
        user = get_object_or_404(User, username=owner)
        plugin.owners.remove(user)
        ConfiguredPlugin.objects.filter(
            plugin_version__plugin__pk=plugin_id).all().delete()
        if user == request.user:
            return redirect('/plugins')

    return redirect('/plugins/ownership/' + str(plugin_id))


class CreateVersionForm(forms.ModelForm):
    code = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'cols': 80,
            'rows': 50,
            'class': 'code'
        }))

    class Meta:
        model = PluginVersion
        fields = [
            'major_version',
            'minor_version',
            'code',
        ]


def get_create_version(request, plugin):
    code = STARTER_CODE
    major_version = 1
    minor_version = 0
    for version in plugin.pluginversion_set.all():
        if (version.major_version > major_version
                or version.major_version == major_version
                and version.minor_version >= minor_version):
            code = version.code
            major_version = version.major_version
            minor_version = version.minor_version + 1

    form = CreateVersionForm({
        'code': code,
        'major_version': major_version,
        'minor_version': minor_version,
    })

    return render(request, 'plugins/update.html', {
        'form': form,
        'plugin': plugin
    })


def post_create_version(request, plugin):
    form = CreateVersionForm(request.POST)
    error = None
    form.is_valid()
    if form.is_valid():
        # TODO: Gross, clean up
        version = form.save(commit=False)
        version_set = plugin.pluginversion_set.all()
        if version_set.filter(major_version__gt=version.major_version).exists():
            error = "A larger major version already exists, incriment major version number"
        elif version_set.filter(
                major_version=version.major_version,
                minor_version=version.minor_version):
            error = "Version already exists, incriment major or minor version number"
        elif (not version.major_version == 1 and not version_set.filter(
                major_version=version.major_version).exists()
              and not version_set.filter(major_version=version.major_version -
                                         1).exists()):
            error = "Major version number skipped, decriment major version number"
        elif (version_set.filter(major_version=version.major_version).exists()
              and not version_set.filter(
                  major_version=version.major_version,
                  minor_version=version.minor_version - 1).exists()):
            error = "Minor version number skipped, decriment minor version number"
        elif (not version_set.filter(
                major_version=version.major_version).exists()
              and version.minor_version != 0):
            error = "The first minor version for a new major version must be 0"
        else:
            version.plugin = plugin
            version.save()
            return redirect('/plugins')
    else:
        error = "Form invalid"

    return render(request, 'plugins/update.html', {
        'form': form,
        'plugin': plugin,
        'error': error,
    })


@login_required
@require_http_methods(["GET", "POST"])
def create_version(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)

    # TODO: Use django permissions to guard against this
    if not plugin.owners.filter(pk=request.user.pk).exists():
        return render(request, 'plugins/not_owner.html', {
            'plugin_name': plugin.name,
            'plugin_owners': plugin.owners.all(),
        })

    if request.method == "GET":
        return get_create_version(request, plugin)

    return post_create_version(request, plugin)


@login_required
@require_http_methods(["POST"])
def update_description(request, plugin_id):
    plugin = get_object_or_404(Plugin, pk=plugin_id)

    form = EditDescriptionForm(request.POST, instance=plugin)
    if form.is_valid():
        form.save()

    return redirect('/plugins')


class EditVersionForm(forms.ModelForm):
    code = forms.CharField(
        label='',
        widget=forms.Textarea(attrs={
            'cols': 80,
            'rows': 50,
            'class': 'code'
        }))

    class Meta:
        model = PluginVersion
        fields = [
            'code',
        ]


def get_edit_version(request, version, error=None):
    form = EditVersionForm(instance=version)

    return render(request, 'plugins/edit.html', {
        'version': version,
        'form': form,
        'error': error,
    })


def post_edit_version(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)

    form = EditVersionForm(request.POST, instance=version)
    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    error = None
    if version.published:
        error = "Plugin already published"
    elif form.is_valid():
        form.save()
    else:
        error = "Invalid form"

    return redirect('/plugins')


@login_required
@require_http_methods(["GET", "POST"])
def edit_version(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)

    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    if request.method == "GET":
        return get_edit_version(request, version)

    return post_edit_version(request, version_id)


@login_required
@require_http_methods(["POST"])
def publish_version(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)

    # TODO: Use django permissions to guard against this
    if not version.plugin.owners.filter(pk=request.user.pk).exists():
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    version.published = True
    version.save()

    return redirect('/plugins')


@login_required
@require_http_methods(["GET"])
def view_version(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)

    if not version.plugin.owners.filter(
            pk=request.user.pk).exists() and not version.approved:
        return render(
            request, 'plugins/not_owner.html', {
                'plugin_name': version.plugin.name,
                'plugin_owners': version.plugin.owners.all(),
            })

    return render(request, 'plugins/view_version.html', {
        'plugin_version': version,
    })


class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(max_length=2048)


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["GET"])
def approvals(request):
    versions = PluginVersion.objects.filter(
        published=True, approved=False, rejected=False)
    return render(request, 'plugins/approvals.html', {
        'versions': versions,
        'rejection_form': RejectionForm(),
    })


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def approve(request, version_id):
    version = get_object_or_404(PluginVersion, pk=version_id)

    version.approved = True
    version.save()

    return redirect('/plugins/approvals')


@user_passes_test(lambda u: u.is_superuser)
@require_http_methods(["POST"])
def reject(request, version_id):
    rejection_form = RejectionForm(request.POST)

    if not rejection_form.is_valid():
        return redirect('/plugins/approvals')

    version = get_object_or_404(PluginVersion, pk=version_id)

    version.rejected = True
    version.rejection_reason = rejection_form.cleaned_data['rejection_reason']
    version.save()

    return redirect('/plugins/approvals')
