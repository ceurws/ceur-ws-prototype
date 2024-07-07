$(document).ready(function () {
    // Hide initial validation errors
    $('.invalid-feedback').hide();

    // Show errors only on submit
    $('#form-container').on('submit', function () {
      $('.invalid-feedback').show();
    });
  });



  $('#add_session').click(function () {
    var form_idx = $('#id_session-TOTAL_FORMS').val();
    $('#session-form').append($('#empty_session_form').html().replace(/__prefix__/g, form_idx));
    $('#id_session-TOTAL_FORMS').val(parseInt(form_idx) + 1);
  });

  $('#add_editor').click(function () {
    var form_idx = $('#id_editor-TOTAL_FORMS').val();
    $('#editor-form').append($('#empty_editor_form').html().replace(/__prefix__/g, form_idx));
    $('#id_editor-TOTAL_FORMS').val(parseInt(form_idx) + 1);
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



