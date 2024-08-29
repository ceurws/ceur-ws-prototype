$(document).ready(function() {
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
      $(document).on('click', deleteButtonClass, function() {
          var parentDiv = $(this).closest(formClass);
          parentDiv.find('input[type=checkbox][name$="-DELETE"]').prop('checked', true); 
          parentDiv.hide(); 
      });
  }
  addForm('#add_preface', '#id_preface-TOTAL_FORMS', '#preface-form', '#empty_preface_form');
  addForm('#add_session', '#id_session-TOTAL_FORMS', '#session-form', '#empty_session_form');
  addForm('#add_editor', '#id_editor-TOTAL_FORMS', '#editor-form', '#empty_editor_form');
  addForm('#add_author', '#id_author-TOTAL_FORMS', '#author-form', '#empty_author_form');
  deleteForm('.delete-preface', '.preface-form');
  deleteForm('.delete-session', '.session-form');
  deleteForm('.delete-editor', '.editor-form');
  deleteForm('.delete-author', '.author-form');
});


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

startDateInput.addEventListener('change', updateEndDateMin);
endDateInput.addEventListener('change', updateStartDateMax);

if (startDateInput.value) {
  updateEndDateMin();
} else if (endDateInput.value) {
  updateStartDateMax();
}

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

$(document).ready(function () {
  function toggleDetails() {
      const $detailsDiv = $(this).parent().next('.paper-details');
      $detailsDiv.toggle();
      $(this).toggleClass('down up');
      paper_id = $(this).attr('title');
      $('#paper_id').val(paper_id);
  }
  $('.toggle-details').on('click', toggleDetails);
});

document.addEventListener('DOMContentLoaded', function () {
var nestedSortables = document.getElementById('nested-sortable');
var sortableLists = document.querySelectorAll('ul[id^="nested-sortable-"], ul[id="nested-sortable-unassigned"]');

function captureInitialState() {
  var order = [];
  sortableLists.forEach(function (nestedSortable) {
      var sessionId = nestedSortable.getAttribute('data-session-id');
      nestedSortable.querySelectorAll('.paper-item').forEach(function (item) {
          order.push({
              paperId: item.getAttribute('data-paper-id'),
              session: sessionId
          });
      });
  });

  if (order.length > 0) {
      var orderInput = document.createElement('input');
      orderInput.type = 'hidden';
      orderInput.name = 'paper_order';
      orderInput.value = JSON.stringify(order);
      document.getElementById('sortable-list').appendChild(orderInput);
  }
}

// Capture initial state on form submit
var form = document.getElementById('sortable-list');
form.addEventListener('submit', captureInitialState);

// Initialize the Sortable for multiple nested sortables if they exist
if (sortableLists.length > 0) {
  sortableLists.forEach(function (nestedSortables) {
      new Sortable(nestedSortables, {
          group: 'nested',
          animation: 150,
          fallbackOnBody: true,
          swapThreshold: 0.65,
          handle: '.handle',
          scroll: true,
          scrollSensitivity: 35, 
          scrollSpeed: 15, 
          bubbleScroll: true,
          forceAutoScrollFallback: true,
          dragOverBubble: true,
          // forceFallback: true, 
          onEnd: function (evt) {
              captureInitialState(); 
          }
      });
  });
}
});