$(document).ready(function () {
  $('.invalid-feedback').hide();

  // Show errors only on submit
  $('#form-container').on('submit', function () {
    $('.invalid-feedback').show();
  });

  function addForm(buttonId, totalFormsId, formContainerId, emptyFormHtmlId) {
    $(buttonId).click(function () {
      var form_idx = $(totalFormsId).val();
      var form_html = $(emptyFormHtmlId).html().replace(/__prefix__/g, form_idx);
      $(formContainerId).append(form_html);
      $(totalFormsId).val(parseInt(form_idx) + 1);
    });
  }

  function deleteForm(deleteButtonClass, formClass) {
    $(document).on('click', deleteButtonClass, function () {
      var parentDiv = $(this).closest(formClass);
      parentDiv.find('input[type=checkbox][name$="-DELETE"]').prop('checked', true);
      parentDiv.hide();
    });
  }

  const startDateInput = document.getElementById('workshop_begin_date');
  const endDateInput = document.getElementById('workshop_end_date');

  function updateEndDateMin() {
    endDateInput.setAttribute('min', startDateInput.value);
    if (endDateInput.value && startDateInput.value) {
      endDateInput.value = startDateInput.value;
    }
  }

  function updateStartDateMax() {
    if (startDateInput.value && startDateInput.value > endDateInput.value) {
      startDateInput.value = endDateInput.value;
    }
  }

  addForm('#add_preface', '#id_preface-TOTAL_FORMS', '#preface-form', '#empty_preface_form');
  addForm('#add_session', '#id_session-TOTAL_FORMS', '#session-form', '#empty_session_form');
  addForm('#add_editor', '#id_editor-TOTAL_FORMS', '#editor-form', '#empty_editor_form');
  addForm('#add_author', '#id_author-TOTAL_FORMS', '#author-form', '#empty_author_form');
  deleteForm('.delete-preface', '.preface-form');
  deleteForm('.delete-session', '.session-form');
  deleteForm('.delete-editor', '.editor-form');
  deleteForm('.delete-author', '.author-form');

  startDateInput.addEventListener('change', updateEndDateMin);
  endDateInput.addEventListener('change', updateStartDateMax);

  if (startDateInput.value) {
    updateEndDateMin();
  } else if (endDateInput.value) {
    updateStartDateMax();
  }
});

function CopyText(elementId, tooltipId) {
  var url = document.getElementById(elementId).href;
  navigator.clipboard.writeText(url).then(() => {
    console.log('Text copied to clipboard');
    var tooltip = document.getElementById(tooltipId);
    tooltip.innerHTML = "Copied to clipboard!";
  });
}

function outFunc(tooltipId) {
  var tooltip = document.getElementById(tooltipId);
  tooltip.innerHTML = "Copy to clipboard";
}

