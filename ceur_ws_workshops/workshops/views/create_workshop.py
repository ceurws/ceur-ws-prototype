from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Editor, Author, Session
from django.urls import reverse
from django.views import View
from ..forms import WorkshopForm, EditorFormSet, AuthorFormSet, PaperForm, SessionFormSet
from django.core.exceptions import ObjectDoesNotExist

class CreateWorkshop(View):
    success_path = "workshops/workshop_edit_success.html"
    overview_path = "workshops/workshop_overview.html"
    edit_path = "workshops/edit_workshop.html"
    
    def get_workshop(self, workshop_id):
        return get_object_or_404(Workshop, id = workshop_id)
    
    def get(self, request):
        form = WorkshopForm()
        editor_form = EditorFormSet(queryset=Editor.objects.none(), 
                                    prefix='editor')
        session_form = SessionFormSet(queryset=Session.objects.none(), 
                                      prefix='session')
        context = {'form':form, 
                   'editor_form':editor_form, 
                   'session_form':session_form}
        return render(request, "workshops/create_workshop.html", context)
    

    def post(self, request):
        if 'submit_button' in request.POST: 
            workshop_instance = self.get_workshop(request.POST.get('workshop_id')) if request.POST.get('workshop_id') else None

            editor_formset = EditorFormSet(queryset=Editor.objects.none(), data=request.POST, prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(), data=request.POST, prefix="session")

            workshop_form = WorkshopForm(data=request.POST, files=request.FILES, instance=workshop_instance)

            if workshop_form.is_valid() and editor_formset.is_valid() and session_formset.is_valid():
                workshop = workshop_form.save()

                editor_instances = editor_formset.save()
                session_instances = session_formset.save()
                workshop.editors.add(*editor_instances)
                workshop.sessions.add(*session_instances)

                # context = {
                #     'organizer_url': reverse('workshops:workshop_overview', args=[workshop.secret_token]),
                #     'author_url': reverse('workshops:author_upload', args=[workshop.author_upload_secret_token])
                # }
                # return render(request, self.success_path, context)
                return redirect('workshops:workshop_overview', secret_token=workshop.secret_token)
            else:
                context = {
                    'form': workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset
                }
                return render(request, self.edit_path, context)

        else:
            workshop_form = WorkshopForm(data=request.POST, files=request.FILES)
            editor_formset = EditorFormSet(queryset=Editor.objects.none(), data=request.POST, prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(), data=request.POST, prefix="session")
            if workshop_form.is_valid() and editor_formset.is_valid() and session_formset.is_valid():
                workshop_instance = workshop_form.save()

                bound_workshop_form = WorkshopForm(instance=workshop_instance)
                context = {
                    'form': bound_workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset,
                    'workshop_instance': workshop_instance
                }
                return render(request, self.edit_path, context)
            else:
                context = {
                    'form': workshop_form,
                    'editor_form': editor_formset,
                    'session_form': session_formset
                }
                return render(request, self.edit_path, context)