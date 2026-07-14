/* Smaart SPL Webviewer — browser console capture snippet
 *
 * What it does: wraps the browser's WebSocket so every message to/from Smaart
 * is recorded in memory, then lets you download them as a JSON file.
 *
 * Note: paste this BEFORE the data starts and it captures the live SPL/LEQ
 * data frames reliably. It may miss the very first "subscribe" command the
 * page sends at connect (that fires before this is installed). To also catch
 * that handshake, use the DevTools Network method in the guide. For just the
 * data format, this snippet is enough.
 *
 * Usage:
 *   1. Open the Smaart SPL Webviewer page (http://<smaart-ip>:26000).
 *   2. Open DevTools console (F12 -> Console), paste this whole file, Enter.
 *   3. Let it run ~60 seconds with audio playing so SPL values move.
 *   4. Run:  splDump()
 *   5. Send the downloaded smaart-capture-*.json file back.
 */
(function () {
  if (window.__splCap) {
    console.log('[SPL capture] already installed. Frames so far:', window.__splCap.length);
    return;
  }
  window.__splCap = [];
  var Native = window.WebSocket;

  function Wrapped(url, protocols) {
    var ws = (protocols !== undefined) ? new Native(url, protocols) : new Native(url);
    window.__splCap.push({ t: Date.now(), dir: 'open', url: String(url) });

    var origSend = ws.send.bind(ws);
    ws.send = function (data) {
      try {
        window.__splCap.push({
          t: Date.now(), dir: 'sent',
          data: (typeof data === 'string') ? data : '[binary ' + (data && data.byteLength) + ' bytes]'
        });
      } catch (e) {}
      return origSend(data);
    };

    ws.addEventListener('message', function (ev) {
      try {
        window.__splCap.push({
          t: Date.now(), dir: 'recv',
          data: (typeof ev.data === 'string') ? ev.data : '[binary]'
        });
      } catch (e) {}
    });
    return ws;
  }

  Wrapped.prototype = Native.prototype;
  Wrapped.CONNECTING = Native.CONNECTING;
  Wrapped.OPEN = Native.OPEN;
  Wrapped.CLOSING = Native.CLOSING;
  Wrapped.CLOSED = Native.CLOSED;
  window.WebSocket = Wrapped;

  window.splDump = function () {
    var blob = new Blob([JSON.stringify(window.__splCap, null, 2)], { type: 'application/json' });
    var a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'smaart-capture-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    console.log('[SPL capture] downloaded', window.__splCap.length, 'frames');
  };

  console.log('[SPL capture] installed. Now: if the page already shows live numbers, just wait ~60s then run splDump(). '
            + 'If numbers are NOT moving yet, reload the page now to (re)connect, wait ~60s, then run splDump().');
})();
