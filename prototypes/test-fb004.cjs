// Executes the exported Code nodes, not n8n's HTTP runtime. No dependencies/network.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
const workflow = JSON.parse(fs.readFileSync(path.join(__dirname, 'fb003-local-api-demo.json')));
const node = name => workflow.nodes.find(n => n.name === name);
function execute(name, data) {
  return JSON.parse(JSON.stringify(vm.runInNewContext(
    `(function(){${node(name).parameters.jsCode}\n})()`,
    {$input: {first: () => ({json: data})}}, {timeout: 1000})[0].json));
}
const valid = {request_id:'final_001', email:'demo@example.org', intent:'support'};
function result(body) { return execute('Mock API Result', execute('Validate Payload', {body})); }
test('inactive four-node local mock graph and dynamic JSON response', () => {
  assert.equal(workflow.active, false);
  assert.equal(workflow.nodes.length, 4);
  assert.deepEqual(workflow.pinData, {});
  const names = ['Webhook','Validate Payload','Mock API Result','Respond to Webhook'];
  names.slice(0,-1).forEach((name,i) => assert.deepEqual(workflow.connections[name].main,
    [[{node:names[i+1],type:'main',index:0}]]));
  assert.equal(node('Webhook').parameters.httpMethod,'POST');
  assert.equal(node('Webhook').parameters.responseMode,'responseNode');
  assert.equal(node('Respond to Webhook').parameters.respondWith,'json');
  assert.equal(node('Respond to Webhook').parameters.responseBody,'={{ JSON.stringify($json.body) }}');
  assert.equal(node('Respond to Webhook').parameters.options.responseCode,'={{ $json.statusCode }}');
  assert.ok(workflow.nodes.every(n => !n.credentials && !n.continueOnFail));
});
for (const [intent,route] of [['support','helpdesk'],['sales','sales-queue'],['other','general']]) {
  test(`valid ${intent}`, () => assert.deepEqual(result({...valid,intent}), {
    statusCode:200,body:{ok:true,request_id:'final_001',provider:'local-mock',result:{route,accepted:true}}
  }));
}
for (const [field,values] of Object.entries({
  intent:['unknown','',null,7,{},['support']],
  email:['bad','a@b','a b@example.org','x'.repeat(255)+'@example.org',null,7,{}],
  request_id:['x','x'.repeat(65),'<script>',null,7,{}]
})) for (const [i,value] of values.entries()) {
  test(`reject ${field} case ${i}`, () => {
    const r = result({...valid,[field]:value});
    assert.equal(r.statusCode,400);
    assert.equal(r.body.ok,false);
    assert.equal(r.body.errors.length,1);
    assert.ok(r.body.errors[0].startsWith(field));
    assert.deepEqual(Object.keys(r.body).sort(),['errors','ok','request_id']);
    assert.equal(r.body.request_id,field==='request_id'?null:'final_001');
  });
}
for (const body of [null,[],{},'text']) test(`reject malformed body ${JSON.stringify(body)}`, () => {
  const r=result(body); assert.equal(r.statusCode,400); assert.equal(r.body.errors.length,3);
});
test('missing body cannot fall back to envelope fields', () => {
  assert.equal(execute('Validate Payload',valid).valid,false);
});
test('request ID boundaries', () => {
  for (const length of [3,64]) assert.equal(result({...valid,request_id:'a'.repeat(length)}).statusCode,200);
});
