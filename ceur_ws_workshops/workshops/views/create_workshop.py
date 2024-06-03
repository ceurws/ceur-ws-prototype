from django.shortcuts import render, get_object_or_404, redirect
from ..models import Workshop, Paper, Editor, Author, Session
from django.urls import reverse
from django.views import View
from ..forms import WorkshopForm, EditorFormSet, AuthorFormSet, PaperForm, SessionFormSet

class CreateWorkshop(View):
    success_path = "workshops/workshop_edit_success.html"
    edit_path = "workshops/edit_workshop.html"
    
    def get_workshop(self, workshop_id):
        workshop = get_object_or_404(Workshop, id = workshop_id)
        return workshop
    
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
        # if statement to check if the submit button has been clicked.
        if 'submit_button' in request.POST:
            workshop_instance = self.get_workshop(request.POST.get('workshop_id'))
            # check if new editor agreement is uploaded
            if bool(request.FILES.get('editor_agreement', False)) == True:
                workshop_form = WorkshopForm(data = request.POST, 
                                             files = request.FILES,
                                             instance = workshop_instance)

                editor_formset = EditorFormSet(queryset=Editor.objects.none(),
                                              data = request.POST, 
                                              prefix="editor")
                session_formset = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")
            
            # if no new editor agreement is uploaded we extract the previous editor agreement
            else:
    
                workshop_form = WorkshopForm(request.POST, instance = workshop_instance)
                editor_formset = EditorFormSet(queryset=Editor.objects.none(),
                                              data = request.POST, 
                                              prefix="editor")
                session_formset = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")

            # Once forms have been bound (either using old or new editor agreement), we validate and save to the database.
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()]):
                workshop = workshop_form.save()  
                
                editor_instances = editor_formset.save()
                session_instances = session_formset.save()
                workshop.editors.add(*editor_instances)
                workshop.sessions.add(*session_instances)

                context = {
                    'organizer_url': reverse('workshops:workshop_overview', args=[workshop.secret_token]),
                    'author_url': reverse('workshops:author_upload', args=[workshop.secret_token])
                }
                return render(request, self.success_path, context)
            else:
                print('problem validating')

        # if no confirm button has been clicked we validate the data first with the user
        else:

            workshop_form = WorkshopForm(data = request.POST, 
                                         files = request.FILES)
            editor_formset = EditorFormSet(queryset=Editor.objects.none(),
                                           data = request.POST, 
                                           prefix="editor")
            session_formset = SessionFormSet(queryset=Session.objects.none(),data = request.POST, prefix="session")
            
            # before rendering we check if the bound forms are valid and we save a workshop instance so that the editor agreement can be extracted in a later stage
            if all([workshop_form.is_valid(), editor_formset.is_valid(), session_formset.is_valid()]):
                workshop_instance = workshop_form.save()  
                
                bound_workshop_form = WorkshopForm(instance = workshop_instance)
                context = {
                           'form' : bound_workshop_form, 
                           'editor_form' : editor_formset, 
                           'session_form' : session_formset,
                           'workshop_instance' : workshop_instance}
                return render(request, self.edit_path, context) 
            
            else:
                # cleanfunction
                context = {'form': workshop_form, 
                           'editor_form':editor_formset, 
                           'session_form':session_formset}
                return render(request, self.edit_path, context)