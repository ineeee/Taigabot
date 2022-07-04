/*
 * why javascript? because:
 *   <ine> adrift: post a programming language
 *   <adrift> js
 *   <ine> ok
 *
 */

const fs = require('fs');

const files = {};
const help_regex = /^([a-z0-9_]+)( <[0-9a-z #@\|\.]+>| \[[0-9a-z #@\|\.]+\])*( -- |: )(.+)$/i;

function process(list, type) {
	for (const [key, cmd] of list) {
		let file = cmd.filename;

		// wipe docstring if its not valid
		// TODO learn regxp.exec(str) vs str.match(regxp)
		if (!help_regex.exec(cmd.help))
			cmd.help = null;

		if (!(file in files))
			files[file] = [];

		cmd.type = type;
		files[file].push(cmd);
	}
}

console.log('reading taigabot data from plugins.json...');
const data = JSON.parse(fs.readFileSync('plugins.json'));
process(Object.entries(data.commands), 'command');
process(Object.entries(data.events), 'event');
process(Object.entries(data.regexes), 'regex');
process(Object.entries(data.sieves), 'sieve');

console.log('writing parsed data to plugins-per-name.json...');
fs.writeFileSync('plugins-per-name.json', JSON.stringify(files, undefined, 2));

/*
 * <ine> can u suggest any css framework thingie prussian?
 * <prussian> Tailwind is hot
 * <prussian> Bulma is ez
 * <prussian> Idk
 * <ine> which one do u want me to use
 * <prussian> https://bulma.io/
 * <ine> ok sure
 */

var html = `
<!DOCTYPE html><html>
<head>
	<meta charset="utf-8">
	<title>Taigabot</title>

	<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bulma/0.9.4/css/bulma.min.css" integrity="sha512-HqxHUkJM0SYcbvxUw5P60SzdOTy/QVwA1JJrvaXJv4q7lmbDZCmZaqz01UPOaQveoxfYRv1tHozWGPMcuTBuvQ==" crossorigin="anonymous" referrerpolicy="no-referrer" />
</head>
<body>
	<section class="section">
`;

const prohibited = {
	'<': '&lt;',
	'>': '&gt;',
	'"': '&quot;',
	'\'': '&#39;',
	'&': '&amp;',
	'`': '&#96;',
};

const prohibited_regexp = new RegExp(Object.keys(prohibited).join('|'), 'g');

function esc(input) {
	return input.replace(prohibited_regexp, (match) => prohibited[match]);
}

const files_sorted = Object.keys(files).sort();

for (const file of files_sorted) {
	const plugins = files[file];

	html += `
	<div class="content">
		<h4>${esc(file)} <small><a href="https://github.com/inexist3nce/Taigabot/blob/dev/${esc(file)}">src</a></small></h4>

		<ul>
	`;

	for (const plugin of plugins) {
		html += `
			<li>
		`;

		if (plugin.type == 'command') {
			html += `
				<p>
					<span class="tag is-primary is-light">cmd</span>
					<span>${esc(plugin.function)}</span>
			`;

			if (plugin.hook.adminonly === true) {
				html += `
					<small class="tag is-light">Global admin only</small>
				`
			} else if (plugin.hook.channeladminonly === true) {
				html += `
					<small class="tag is-light">Channel admin only</small>
				`
			}

			html += `
				</p>

				<ul>
			`;

			for (const tag of plugin.triggers) {
				let help = '';

				if (plugin.help !== null) {
					help = esc(plugin.help);

					if (help.startsWith(plugin.function))
						help = help.replace(plugin.function, '');
					else
						help = '<i class="has-text-grey">Cannot parse help</i>';
				} else {
					help = '<i class="has-text-grey">No help available</i>'
				}


				html += `
					<li>
						<span><strong>.${esc(tag)}</strong> ${help}</span>
					</li>
				`;
			}

			html += `
				</ul>

				<p>&nbsp;</p>
			`;
		} else if (plugin.type == 'event') {
			html += `
				<p>
					<span class="tag is-info is-light">event</span>
					<span>${esc(plugin.function)}</span>
				</p>
			`;
		} else if (plugin.type == 'regex') {
			html += `
				<p>
					<span class="tag is-success is-light">regexp</span>
					<span>${esc(plugin.function)}</span>
				</p>
			`;
		} else if (plugin.type == 'sieve') {
			html += `
				<p>
					<span class="tag is-warning is-light">sieve</span>
					<span>${esc(plugin.function)}</span>
				</p>
			`;
		} else {
			html += `
				<p>
					<span class="tag is-danger is-light">unknown</span>
					<span>${esc(plugin.function)}</span>
				</p>
			`;
		}
		html += `
			</li>
		`;
	}

	html += `
		</ul>
	</div>
	`;
}

html += `
	</section>
</body>
`;

console.log('shitting out plugins.html...');
fs.writeFileSync('plugins.html', html);
