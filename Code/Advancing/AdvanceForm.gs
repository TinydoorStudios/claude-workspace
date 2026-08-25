/**
 * 3CDC Band Advancing — Google Form intake (bridge to n8n)
 * ------------------------------------------------------------
 * Google's ONLY job is the form UI. On each submit, Apps Script POSTs the
 * response to an n8n webhook; n8n owns the database, the .docx, and the tracker.
 *
 * This script builds the generic WP / FSQ / ESP form (from CONFIG) and wires the
 * onSubmit webhook. Re-running setup() reuses the same Form + Sheet (stable URLs).
 *
 * SETUP:
 *   - script.google.com → new project → paste this file.
 *   - Set CONFIG.n8nWebhookUrl (the Production URL of the n8n Webhook node) and CONFIG.uploadEmail.
 *   - Run setup() once, approve the prompt.
 *   - Logs print the Form URL to share with bands + the raw-responses Sheet URL.
 *   - Send a test submission; confirm it lands in n8n.
 */

const CONFIG = {
  formTitle: '3CDC Band Advancing',
  productionManager: 'Kayla',
  advancingContact: 'Brian Lloyd (315-404-5648)',

  venues: ['Washington Park', 'Fountain Square', 'Elm Street Plaza'],

  // Dedicated inbox bands email their stage plot + input list to.
  uploadEmail: 'REPLACE_ME@gmail.com',

  // n8n Webhook node Production URL, e.g. https://n8n.tinydoorstudios.com/webhook/advancing
  n8nWebhookUrl: 'REPLACE_ME',
  // Optional shared secret; must match the n8n workflow's check.
  webhookSecret: 'CHANGE_ME',

  dbLimit: 95,
  privateTentOffered: true,
};

const PROP = { FORM: 'ADV_FORM_ID', SS: 'ADV_SS_ID' };

function setup() {
  const props = PropertiesService.getScriptProperties();
  const ss = getOrCreateSpreadsheet_(props);         // raw-response backup log
  const form = buildForm_(props);
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  clearTriggers_();
  ScriptApp.newTrigger('onFormSubmit').forForm(form).onFormSubmit().create();

  Logger.log('SETUP COMPLETE');
  Logger.log('Form (share with bands): ' + form.getPublishedUrl());
  Logger.log('Form editor: ' + form.getEditUrl());
  Logger.log('Raw responses backup: ' + ss.getUrl());
  Logger.log('Webhook target: ' + CONFIG.n8nWebhookUrl);
}

// --- onSubmit: POST the response to n8n --------------------
function onFormSubmit(e) {
  const data = responseToMap_(e.response);
  const payload = {
    secret: CONFIG.webhookSecret,
    submittedAt: new Date().toISOString(),
    email: data['__email'],
    venue: data['Venue'],
    act: data['Act / band name'],
    date: data['Show date'],
    fields: data,
  };
  UrlFetchApp.fetch(CONFIG.n8nWebhookUrl, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload),
    muteHttpExceptions: true,
  });
}

// --- Form builder -----------------------------------------
function buildForm_(props) {
  let form;
  const existingId = props.getProperty(PROP.FORM);
  if (existingId) {
    try { form = FormApp.openById(existingId); form.deleteAllResponses(); clearItems_(form); }
    catch (e) { form = null; }
  }
  if (!form) {
    form = FormApp.create(CONFIG.formTitle);
    props.setProperty(PROP.FORM, form.getId());
  }

  form.setTitle(CONFIG.formTitle)
      .setDescription(
        'Welcome, and thanks for playing with 3CDC.\n\n' +
        'This form replaces the reply-all advancing email. Pick your venue, read each section, ' +
        'acknowledge the policies, and answer the questions — about 5 minutes. Your advancing ' +
        'contact is ' + CONFIG.advancingContact.split('(')[0].trim() + '; questions go to ' +
        CONFIG.productionManager + '.')
      .setCollectEmail(true)
      .setProgressBar(true)
      .setAllowResponseEdits(true)
      .setConfirmationMessage(
        'Got it — thank you. Reopen this link anytime to edit. Don’t forget to email your ' +
        'stage plot & input list to ' + CONFIG.uploadEmail + '.');

  sectionHeader_(form, 'Your show', 'The essentials so we can match you to the booking.');
  form.addListItem().setTitle('Venue').setChoiceValues(CONFIG.venues).setRequired(true);
  form.addTextItem().setTitle('Act / band name').setRequired(true);
  form.addTextItem().setTitle('Show date').setHelpText('e.g. Fri Jun 19, 2026').setRequired(true);
  form.addTextItem().setTitle('Advancing contact — your name').setRequired(true);
  form.addTextItem().setTitle('Best phone to reach the band day-of')
      .setHelpText('We send a morning group text with everyone in the loop (late arrivals, weather).')
      .setRequired(true);
  form.addTextItem().setTitle('Total number of performers')
      .setHelpText('Drives drink tickets, water, and wristband count.')
      .setValidation(FormApp.createTextValidation().requireNumber().build())
      .setRequired(true);

  sectionHeader_(form, 'Load-in & parking',
    'Detailed load-in and parking instructions come with your booking — including any parking ' +
    'validations to distribute to your members. On arrival, text/call your day-of contact when ' +
    '~5 min out and introduce yourself to the stage crew.');
  ackItem_(form, 'I’ve reviewed the load-in & parking instructions for my booking and will ' +
    'distribute any parking validations to my band.');
  yesNo_(form, 'Do you need large-vehicle parking?', true);
  form.addTextItem().setTitle('If yes — vehicle type / size').setRequired(false);

  sectionHeader_(form, 'Technical',
    'We provide a FOH engineer, a monitor engineer, and a stagehand. Artists provide all ' +
    'instruments (including amps and ¼” cables).\n\n' +
    'STAGE PLOT & INPUT LIST: email them (PDF preferred) to ' + CONFIG.uploadEmail +
    ' — put your band name in the file name. Then confirm below.');
  ackItem_(form, 'I’ve emailed (or will email) my current stage plot & input list to ' +
    CONFIG.uploadEmail + '.');
  form.addTextItem().setTitle('Stage plot / input list — link (optional)')
      .setHelpText('Prefer a link? Paste a Drive/Dropbox link set to "anyone with the link can view."')
      .setRequired(false);
  form.addParagraphTextItem().setTitle('Monitor needs')
      .setHelpText('How many mixes, and wedges vs. in-ears? e.g. "4 wedge mixes: vox, timbales, piano, bass."')
      .setRequired(true);
  yesNo_(form, 'Are you bringing your own engineer?', true);
  form.addTextItem().setTitle('If yes — engineer name & what they’re mixing (FOH/MON)')
      .setHelpText('Own engineers need advance coordination and still mix within the ' +
        CONFIG.dbLimit + ' dB limit.').setRequired(false);

  sectionHeader_(form, 'Hospitality & site', 'Merch, band space, and stage access.');
  yesNo_(form, 'Are you selling merch?', true)
    .setHelpText('If yes, you provide the seller, POS, and bank. We provide a tent, table, and chairs by the stage.');
  if (CONFIG.privateTentOffered) {
    yesNo_(form, 'Would you like a 10x10 private tent with sidewalls?', true)
      .setHelpText('Private band space option where indoor dressing rooms aren’t available.');
  }
  form.addTextItem().setTitle('Total wristbands needed')
      .setHelpText('Band members + any guests allowed onstage. Wristbands are required for stage access.')
      .setValidation(FormApp.createTextValidation().requireNumber().build())
      .setRequired(true);
  form.addTextItem().setTitle('Band representative with stage-escort ability — name')
      .setHelpText('One person who can escort guests on/off stage.').setRequired(true);
  yesNo_(form, 'Any special guest performers?', true)
    .setHelpText('Must be pre-approved by 3CDC in this advance.');
  form.addTextItem().setTitle('If yes — who, and doing what?').setRequired(false);

  sectionHeader_(form, 'Policies — please acknowledge',
    'Failure to comply may result in a warning, or termination of the show with payment canceled ' +
    'or delayed. Acknowledge each below.');
  ackItem_(form, 'CONTENT: family-friendly only — no foul language or gestures, including tracks, ' +
    'live vocals, and sound check.');
  ackItem_(form, 'SOUND: strict ' + CONFIG.dbLimit + ' dB limit measured at FOH; house or talent ' +
    'engineers are held to it, and we may baffle amps to reduce stage volume.');
  ackItem_(form, 'PERFORMER SAFETY: stay on the stage — no crowd surfing, climbing, jumping off, or ' +
    'stepping on sound equipment.');
  ackItem_(form, 'AUDIENCE SAFETY: throw or shoot NOTHING into the crowd — no confetti, shirts, ' +
    'bottles, CDs/merch, etc.');
  ackItem_(form, 'WEATHER: rain-or-shine venue. Booking evaluates weather ~3 hrs before start; if you ' +
    'don’t hear otherwise, assume the show goes on.');
  ackItem_(form, 'PAYMENT: all groups are paid AFTER the performance, not before.');

  sectionHeader_(form, 'Anything else', 'Questions, concerns, or requests — put them here.');
  form.addParagraphTextItem().setTitle('Notes / questions').setRequired(false);
  ackItem_(form, 'I confirm the information above is accurate to the best of my knowledge.');

  return form;
}

// --- helpers ----------------------------------------------
function getOrCreateSpreadsheet_(props) {
  const id = props.getProperty(PROP.SS);
  if (id) { try { return SpreadsheetApp.openById(id); } catch (e) {} }
  const ss = SpreadsheetApp.create('Advancing — raw responses');
  props.setProperty(PROP.SS, ss.getId());
  return ss;
}
function sectionHeader_(form, title, help) { form.addPageBreakItem().setTitle(title).setHelpText(help || ''); }
function ackItem_(form, text) {
  return form.addCheckboxItem().setTitle('ACK: ' + text)
    .setChoiceValues(['I have read and understand']).setRequired(true);
}
function yesNo_(form, title, required) {
  return form.addMultipleChoiceItem().setTitle(title).setChoiceValues(['Yes', 'No']).setRequired(!!required);
}
function responseToMap_(response) {
  const map = { '__email': response.getRespondentEmail() || '' };
  response.getItemResponses().forEach(function (ir) {
    let val = ir.getResponse();
    if (Array.isArray(val)) val = val.join(', ');
    map[ir.getItem().getTitle()] = val;
  });
  return map;
}
function clearItems_(form) {
  const items = form.getItems();
  for (let i = items.length - 1; i >= 0; i--) form.deleteItem(items[i]);
}
function clearTriggers_() {
  ScriptApp.getProjectTriggers().forEach(function (t) { ScriptApp.deleteTrigger(t); });
}
