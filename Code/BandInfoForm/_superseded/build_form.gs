/**
 * 3CDC Band Advance Form — rough test build.
 *
 * HOW TO RUN:
 *   1. Go to https://script.google.com  ->  New project
 *   2. Delete the stub code, paste this whole file in.
 *   3. Hit Run (select buildForm). Approve the permission prompt the first time.
 *   4. The Execution log prints the live form URL + the edit URL.
 *
 * NOTE ON FILE UPLOAD:
 *   Google Forms file-upload questions require the respondent to be signed
 *   into a Google account, and the form must live in a Workspace domain.
 *   Bands without a Google login can't use the upload. That's why stage plot
 *   is BOTH an upload (optional) AND a text/link description (optional) —
 *   they use whichever works for them.
 */

function buildForm() {
  var form = FormApp.create('3CDC — Band Advance / Show Details')
    .setDescription(
      'Please complete this so we have everything we need to run your show. ' +
      'One submission per performance. Questions? Reply to your booking contact.'
    )
    .setCollectEmail(true)
    .setProgressBar(true)
    .setAllowResponseEdits(true);

  // ---------- SECTION 1: BASICS ----------
  form.addSectionHeaderItem()
    .setTitle('Show Basics');

  form.addTextItem()
    .setTitle('Band / Group Name')
    .setRequired(true);

  form.addListItem()
    .setTitle('Venue')
    .setChoiceValues([
      'Fountain Square',
      'Washington Park',
      'Elm Street Plaza',
      'Court Street Plaza',
      'Zeigler Park',
      'Imagination Alley'
    ])
    .setRequired(true);

  form.addDateItem()
    .setTitle('Show Date')
    .setRequired(true);

  form.addTextItem()
    .setTitle('Performer Contact — best day-of phone number')
    .setHelpText('Cell phone for the best point of contact from the performing group. ' +
                 'Please text/call your day-of contact when you are ~5 minutes out.')
    .setRequired(true);

  // ---------- SECTION 2: TECHNICAL ----------
  form.addPageBreakItem()
    .setTitle('Technical Details');

  // Stage plot — upload OR describe
  form.addSectionHeaderItem()
    .setTitle('Stage Plot / Input List')
    .setHelpText('Upload a current stage plot / input list, OR describe your setup ' +
                 'below (or paste a link). Either one is fine.');

  var upload = form.addFileUploadItem()
    .setTitle('Stage Plot / Input List — file upload (optional)')
    .setHelpText('PDF, image, or doc. Requires a Google sign-in to upload.');
  upload.setRequired(false);

  form.addParagraphTextItem()
    .setTitle('Stage Plot / Input List — description or link (optional)')
    .setHelpText('If you can\'t upload, describe your input list / stage layout here, ' +
                 'or paste a shareable link.');

  form.addMultipleChoiceItem()
    .setTitle('Do you prefer a flat stage or a drum riser?')
    .setChoiceValues(['Flat stage', 'Drum riser'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Backline / Instrumentation')
    .setHelpText('Artists provide all instruments (including amps and 1/4" cables). ' +
                 'If you\'ve coordinated to SHARE backline with another artist on the ' +
                 'event, tell us here.');

  form.addTextItem()
    .setTitle('How many monitors do you need?')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Are you bringing your own sound engineer?')
    .setHelpText('We provide engineers to mix FOH + monitors. If you plan to bring your ' +
                 'own, coordinate in advance.')
    .setChoiceValues(['No — use house engineers', 'Yes — bringing our own (we\'ll coordinate)'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Scenic — backdrop or scenic elements?')
    .setHelpText('Anything on stage we should be aware of?');

  form.addParagraphTextItem()
    .setTitle('Lighting requests')
    .setHelpText('We provide a house LD. Any specific requests? We\'ll do our best.');

  form.addCheckboxItem()
    .setTitle('95 dB / stage volume — acknowledgment')
    .setHelpText('All sound engineers must mix within the 95 dB city ordinance (measured ' +
                 'at FOH). The FSQ audio engineer reserves the right to baffle amplifiers ' +
                 'to reduce stage volume if necessary.')
    .setChoiceValues(['I understand and acknowledge.'])
    .setRequired(true);

  // ---------- SECTION 3: HOSPITALITY & SITE ----------
  form.addPageBreakItem()
    .setTitle('Hospitality & Site Details');

  form.addMultipleChoiceItem()
    .setTitle('Are you planning to sell merch?')
    .setHelpText('If yes, you provide the seller, point of sale, and bank. We provide a ' +
                 'tent next to the stage with a table and chairs.')
    .setChoiceValues(['Yes', 'No'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Do you want a private band tent? (10x10 with sidewalls)')
    .setHelpText('We have no indoor dressing rooms. On request we can provide a 10x10 ' +
                 'tent with sidewalls for private band space.')
    .setChoiceValues(['Yes, please provide the tent', 'No, not needed'])
    .setRequired(true);

  form.addTextItem()
    .setTitle('Total number of performers')
    .setHelpText('Drink tickets and water are provided — confirm your total headcount.')
    .setRequired(true);

  // ---------- SECTION 4: ACKNOWLEDGMENTS ----------
  form.addPageBreakItem()
    .setTitle('Load-In, Parking & Requirements');

  form.addCheckboxItem()
    .setTitle('Load-in & parking document — acknowledgment')
    .setHelpText('The load-in process at Fountain Square has changed. Please review the ' +
                 'document your contact sent and acknowledge. Garage clearance is 6\'8". ' +
                 'Each vehicle needs its own parking QR validation before arriving.')
    .setChoiceValues(['I have reviewed the load-in / parking document.'])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Performance Requirements — acknowledgment')
    .setHelpText(
      'Failure to comply may result in a warning or termination of the show with payment ' +
      'canceled or delayed. By checking, you acknowledge:\n' +
      '• CONTENT: Family-friendly only (no foul language or gestures) — applies to ' +
      'tracks, live vocals, and sound check.\n' +
      '• SOUND LIMIT: Strict 95 dB limit, measured at FOH, for all engineers.\n' +
      '• PERFORMER SAFETY: Stay on the stage. No crowd surfing, climbing, jumping off ' +
      'stage, or stepping on sound equipment.\n' +
      '• AUDIENCE SAFETY: Do not throw or shoot anything into the crowd (confetti, ' +
      't-shirts, bottles, merch/CDs, etc.).\n' +
      '• WEATHER: Rain or shine. Booking evaluates weather ~3 hrs before start. If you ' +
      'don\'t hear otherwise, assume the show goes on.\n' +
      '• PAYMENT: All groups are paid AFTER the performance, not before.'
    )
    .setChoiceValues(['I have read and acknowledge all performance requirements.'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Additional questions or concerns?')
    .setHelpText('Anything else we should know.');

  Logger.log('LIVE (share this):  ' + form.getPublishedUrl());
  Logger.log('EDIT (your copy):   ' + form.getEditUrl());
}
