const $ = (id) => document.getElementById(id);
const page = document.body.dataset.page;
let csrf = null, busy = false, requestVersion = 0, nextCursor = null;
let cursors = [null], filters = new URLSearchParams({limit: '25'});
let linkSession = null, linkCursors = [null], linkNext = null;
const labels = {document_id:'Document',version_id:'Version',job_id:'Job',session_id:'Session',
  app_id:'App',owner_id:'Owner',filename:'Filename',content_type:'Format',size_bytes:'Bytes',
  state:'State',status:'Status',progress:'Progress',attempts:'Attempts',max_attempts:'Max attempts',
  has_error:'Error recorded',updated_at:'Updated',external_session_id:'External session',
  scope_revision:'Revision',created_at:'Created',deleted_at:'Deleted',active_generation_id:'Active generation',
  generation_id:'Generation',chunk_count:'Chunks',index_fingerprint:'Index revision',
  pipeline_fingerprint:'Pipeline revision',link_id:'Link',attached_at:'Attached',detached_at:'Detached'};
const columns = {
  documents:['filename','state','content_type','size_bytes','app_id','owner_id','document_id','version_id','active_generation_id','created_at'],
  jobs:['state','progress','attempts','max_attempts','has_error','app_id','owner_id','job_id','version_id','updated_at'],
  sessions:['status','external_session_id','scope_revision','app_id','owner_id','session_id','created_at','deleted_at'],
  index:['state','chunk_count','generation_id','version_id','index_fingerprint','pipeline_fingerprint','app_id','owner_id','created_at'],
  links:['status','document_id','version_id','link_id','attached_at','detached_at'],
};
// The API escapes display metadata. Decode only those entities, then use text nodes.
function display(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value).replace(/&(lt|gt|quot|#x27|amp);/g, (_, key) =>
    ({lt:'<',gt:'>',quot:'"','#x27':"'",amp:'&'})[key]);
}
function el(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = display(text);
  if (className) node.className = className;
  return node;
}
function message(text = '', error = '') {
  $('status').textContent = text;
  $('error').textContent = error;
  $('error').hidden = !error;
}
function signedOut(text) {
  csrf = null; requestVersion++;
  $('dashboard').hidden = true; $('logout').hidden = true; $('login').hidden = false;
  $('content')?.replaceChildren(); $('links-content').replaceChildren();
  $('links-panel').hidden = true; linkSession = null;
  if ($('confirmation').open) $('confirmation').close('expired');
  message(text);
}
async function api(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 12000);
  try {
    const response = await fetch('/v1/admin/' + path, {
      ...options, credentials:'same-origin', cache:'no-store', signal:controller.signal,
      headers:{...(options.body ? {'Content-Type':'application/json'} : {}),
        ...(options.method && options.method !== 'GET' && csrf ? {'X-CSRF-Token':csrf} : {}),
        ...options.headers},
    });
    if (!response.ok) {
      const data = await response.json().catch(() => ({}));
      if (response.status === 401 && path !== 'auth/login') {
        signedOut('Your admin session expired. Sign in again.');
        $('username').focus();
      }
      const codes = {invalid_credentials:path === 'auth/login' ? 'Incorrect username or password.' : 'Your admin session expired. Sign in again.',csrf_failed:'Security check failed. Sign out and sign in again.',
        invalid_transition:'This operation is no longer allowed in the current state. Refresh the list.',
        dependency_unavailable:'Administration is unavailable. Check local configuration and dependencies.',
        rate_limited:'Too many sign-in attempts. Wait at least 60 seconds before retrying.',
        invalid_request:'Check the filter values and try again.',not_found:'This metadata record is no longer available.'};
      throw new Error((codes[data.error?.code] || 'Request could not be completed.') +
        ` (HTTP ${response.status}${data.request_id ? '; request ' + data.request_id : ''})`);
    }
    return response.status === 204 ? null : await response.json();
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The local API timed out. Try Refresh now.');
    if (error instanceof TypeError) throw new Error('Cannot reach the local API. Check the connection and try again.');
    throw error;
  } finally { clearTimeout(timer); }
}
function button(text, action, danger = false) {
  const node = el('button', text, danger ? 'danger' : '');
  node.type = 'button'; node.addEventListener('click', action); return node;
}
function confirmOperation(text) {
  return new Promise((resolve) => {
    $('confirm-description').textContent = text;
    $('confirmation').addEventListener('close', () => resolve($('confirmation').returnValue === 'accept'), {once:true});
    $('confirmation').returnValue = ''; $('confirmation').showModal();
  });
}
$('confirm-cancel').onclick = () => $('confirmation').close('cancel');
$('confirm-accept').onclick = () => $('confirmation').close('accept');
async function mutate(path, method, description, trigger) {
  if (busy || !await confirmOperation(description) || !csrf) return;
  busy = true; trigger.disabled = true; message('Submitting operation…');
  try {
    const result = await api(path, {method});
    message('Operation accepted. Audit request: ' + result.request_id);
    busy = false;
    await load(false, true);
    if (linkSession) await loadLinks();
    $('refresh').focus();
  } catch (error) { message('', error.message); }
  finally { busy = false; trigger.disabled = false; }
}
function actions(row, resource) {
  const box = el('div', undefined, 'actions');
  function operation(label, path, method, explanation, danger = false) {
    const control = button(label, () => mutate(path, method, explanation, control), danger);
    box.append(control);
  }
  if (resource === 'jobs') {
    const path = `jobs/${row.job_id}/`;
    if (row.state === 'failed' && row.attempts < row.max_attempts) operation('Retry',path+'retry','POST',`Retry job ${row.job_id}? This queues ingestion using the registered source.`);
    if (['queued','fetching','parsing','chunking','embedding','indexing'].includes(row.state)) operation('Cancel',path+'cancel','POST',`Cancel job ${row.job_id}? Published data and source files are retained.`,true);
    if (row.state === 'ready') operation('Reindex',path+'reindex','POST',`Reindex job ${row.job_id}? This queues processing. The published generation remains until replacement succeeds.`);
  }
  if (resource === 'sessions') {
    box.append(button('View links', async () => {
      if (busy) return;
      linkSession = row.session_id; linkCursors = [null]; $('links-panel').hidden = false;
      await loadLinks(); $('close-links').focus();
    }));
    if (row.status === 'active') operation('Tombstone',`sessions/${row.session_id}`,'DELETE',`Tombstone session ${row.session_id}? Its links become inactive and its scope revision changes. Source files and index data are retained.`,true);
  }
  if (resource === 'links' && row.status === 'attached') operation('Detach',`sessions/${linkSession}/documents/${row.document_id}`,'DELETE',`Detach document ${row.document_id} from this session? Other sessions and source files are retained.`,true);
  if (!box.children.length) box.append(el('span','—'));
  return box;
}
function table(items, resource, target) {
  target.replaceChildren();
  if (!items.length) {
    const empty = el('section', undefined,'panel empty'); empty.append(el('h2','No matching metadata'),el('p','Try different filters or refresh after documents are registered.'));
    target.append(empty); return;
  }
  const wrap = el('div',undefined,'table-wrap'); wrap.tabIndex = 0;
  wrap.setAttribute('role','region'); wrap.setAttribute('aria-label','Scrollable '+resource+' table');
  const t = el('table'); t.append(el('caption',resource === 'links' ? 'Session document links' : 'Current '+resource+' metadata'));
  const head = el('thead'), headRow = el('tr');
  const hasActions = ['jobs','sessions','links'].includes(resource);
  for (const key of [...columns[resource], ...(hasActions ? ['actions'] : [])]) {
    const th = el('th',key === 'actions' ? 'Actions' : labels[key]); th.scope='col'; headRow.append(th);
  }
  head.append(headRow); t.append(head);
  const body = el('tbody');
  for (const row of items) {
    const tr = el('tr');
    for (const key of columns[resource]) {
      const td = el('td');
      if (key === 'state' || key === 'status') td.append(el('span',row[key],'badge'));
      else if (key === 'progress') {
        const progress = el('progress'); progress.max=100; progress.value=row[key];
        progress.setAttribute('aria-label','Job progress');td.append(progress,el('div',row[key]+'%'));
      } else td.append(el('span',row[key],key.endsWith('_id') || key.endsWith('fingerprint') ? 'identifier' : ''));
      tr.append(td);
    }
    if (hasActions) { const td = el('td'); td.append(actions(row,resource)); tr.append(td); }
    body.append(tr);
  }
  t.append(body); wrap.append(t); target.append(wrap);
}
function overview(data) {
  const content = $('content'); content.replaceChildren();
  const cards = el('div',undefined,'cards');
  for (const [key,label] of [['documents','Documents'],['sessions','Sessions'],['generations','Generations'],['chunks','Indexed chunks']]) {
    const card=el('div',undefined,'card'); card.append(el('p',label),el('strong',data.counts[key])); cards.append(card);
  }
  content.append(cards);
  const grid=el('div',undefined,'overview-grid');
  function panel(title, entries) {
    const section=el('section',undefined,'panel'); section.append(el('h2',title));
    for (const [label,value] of entries) { const row=el('div',undefined,'metric-row'); row.append(el('span',label),el('strong',value));section.append(row); }
    grid.append(section);
  }
  panel('Dependency health',Object.entries(data.health.components));
  panel('Ingestion jobs',data.jobs.length ? data.jobs.map(j=>[j.state,j.count]) : [['Jobs','No jobs registered']]);
  panel('Queue & storage',[
    ['Pending durable outbox',data.counts.pending_outbox],['Broker queue depth',data.broker_queue_depth ?? 'Not measured'],
    ['Metadata database (bytes)',data.sizes.metadata_database_bytes],['Registered sources (bytes)',data.sizes.registered_source_bytes],['Vector size (bytes)',data.vector_bytes ?? 'Not measured']]);
  content.append(grid);
}
function pageButtons() {
  if (!$('previous')) return;
  $('previous').disabled = busy || cursors.length === 1;
  $('next').disabled = busy || !nextCursor;
  $('page-number').textContent = 'Page '+cursors.length;
}
async function load(silent = false, keepMessage = false) {
  if (!csrf || busy || page === 'evaluations') return;
  busy = true; const version = ++requestVersion; pageButtons();
  const content = $('content'); content.setAttribute('aria-busy','true');
  $('refresh').disabled = true;
  if (!silent && !keepMessage) message('Loading current metadata…');
  try {
    const query = new URLSearchParams(filters);
    if (cursors.at(-1)) query.set('cursor',cursors.at(-1));
    const data = await api(page === 'overview' ? 'overview' : page+'?'+query);
    if (version !== requestVersion || !csrf) return;
    if (page === 'overview') overview(data); else { table(data.items,page,content); nextCursor = data.next_cursor; }
    $('updated').textContent = 'Last updated '+new Date().toLocaleTimeString()+' · Live local API';
    if (!keepMessage) message('Current metadata loaded.');
  } catch (error) {
    if (version === requestVersion) { content.replaceChildren(); $('updated').textContent='Current data unavailable'; nextCursor=null; }
    message('',error.message);
  } finally { busy=false;content.setAttribute('aria-busy','false');$('refresh').disabled=false;pageButtons(); }
}
async function loadLinks() {
  const session = linkSession;
  if (!session || !csrf) return;
  $('links-previous').disabled=true; $('links-next').disabled=true;
  $('links-content').setAttribute('aria-busy','true');
  try {
    const query=new URLSearchParams({limit:'25'});
    if(linkCursors.at(-1))query.set('cursor',linkCursors.at(-1));
    const data=await api(`sessions/${session}/documents?`+query);
    if (session !== linkSession || !csrf) return;
    $('links-title').textContent='Session documents · '+session;
    table(data.items,'links',$('links-content'));linkNext=data.next_cursor;
    $('links-previous').disabled=linkCursors.length===1;$('links-next').disabled=!linkNext;
  } catch(error){$('links-content').replaceChildren();message('',error.message);}
  finally{$('links-content').setAttribute('aria-busy','false');}
}
async function signedIn() {
  $('login').hidden=true; $('dashboard').hidden=false; $('logout').hidden=false;
  $('password').value='';
  if(page==='evaluations') { message('No evaluation reports available.');$('refresh').hidden=true;$('auto-refresh').parentElement.hidden=true; }
  else await load();
}
$('login-form').addEventListener('submit',async(event)=>{
  event.preventDefault();const submit=event.submitter;submit.disabled=true;message('Signing in…');
  try {
    const data=await api('auth/login',{method:'POST',body:JSON.stringify({username:$('username').value,password:$('password').value})});
    csrf=data.csrf_token; await signedIn(); $('page-title').tabIndex=-1;$('page-title').focus();
  } catch(error){message('',error.message);}
  finally{$('password').value='';submit.disabled=false;}
});
$('logout').onclick=async()=>{
  if(busy)return;busy=true;
  try{await api('auth/logout',{method:'POST'});signedOut('Signed out.');$('username').focus();}
  catch(error){message('',error.message);}finally{busy=false;}
};
$('refresh').onclick=()=>load();
$('filters')?.addEventListener('submit',(event)=>{
  event.preventDefault();if(busy)return;
  filters=new URLSearchParams();
  for(const [key,value] of new FormData(event.target))if(value)filters.set(key,value);
  cursors=[null];load();
});
$('clear-filters')?.addEventListener('click',()=>{if(busy)return;$('filters').reset();filters=new URLSearchParams({limit:'25'});cursors=[null];load();});
$('next')?.addEventListener('click',()=>{if(busy||!nextCursor)return;cursors.push(nextCursor);load();});
$('previous')?.addEventListener('click',()=>{if(busy||cursors.length===1)return;cursors.pop();load();});
$('links-next').onclick=()=>{if(linkNext){linkCursors.push(linkNext);loadLinks();}};
$('links-previous').onclick=()=>{if(linkCursors.length>1){linkCursors.pop();loadLinks();}};
$('close-links').onclick=()=>{linkSession=null;$('links-panel').hidden=true;$('refresh').focus();};
setInterval(async()=>{
  if(!csrf||busy||document.hidden||$('confirmation').open)return;
  // Check expiry even on the evaluation empty screen. Avoid replacing keyboard targets.
  try{await api('auth/session');}catch(error){message('',error.message);return;}
  if($('auto-refresh').checked&&!$('content')?.contains(document.activeElement)&&!$('links-panel').contains(document.activeElement))await load(true);
},15000);
try{const data=await api('auth/session');csrf=data.csrf_token;await signedIn();}
catch(error){signedOut('Sign in to view operational metadata.');if(!error.message.includes('HTTP 401'))message('',error.message);}
