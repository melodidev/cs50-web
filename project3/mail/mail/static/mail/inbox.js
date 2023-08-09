document.addEventListener('DOMContentLoaded', function() {

	// Use buttons to toggle between views
	document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
	document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
	document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
	document.querySelector('#compose').addEventListener('click', compose_email);

	// By default, load the inbox
	load_mailbox('inbox');
});

document.querySelector('#compose-form').addEventListener('submit', function() {
	event.preventDefault();
	send_email();
});

function compose_email() {

	// Show compose view and hide other views
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#display-email').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'block';

	// Clear out composition fields
	document.querySelector('#compose-recipients').value = '';
	document.querySelector('#compose-subject').value = '';
	document.querySelector('#compose-body').value = '';
}

function send_email() {
	let data = {
		recipients: document.querySelector('#compose-recipients').value,
		subject: document.querySelector('#compose-subject').value,
		body: document.querySelector('#compose-body').value
	}

	// Upload JSON data
	fetch('/emails', {
		method: "POST",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify(data)
	})
	.then(response => response.json())
	// Check if the fetch is successful
	.then(data => {
		console.log("Success:", data);
		// Load the user’s sent mailbox
		load_mailbox('sent');
	})
	.catch((error) => {
		console.error(error);
	});
}

function load_mailbox(mailbox) {
	
	// Show the mailbox and hide other views
	document.querySelector('#emails-view').style.display = 'block';
	document.querySelector('#compose-view').style.display = 'none';
	document.querySelector('#display-email').style.display = 'none';

	// Show the mailbox name
	document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

	// Load a particular mailbox
	fetch(`/emails/${mailbox}`)
	.then(response => response.json())
	.then(array => {
		array.forEach(element => {
			let line = document.createElement('div');
			if (element.read) {
				line.className = "read";
			}

			if (mailbox == "sent") {
				line.innerHTML =`to ${element.recipients} ${element.subject} ${element.timestamp}`;
			} else {
				line.innerHTML =`${element.sender} ${element.subject} ${element.timestamp}`;
			}

			line.addEventListener('click', function () {
				view_email(mailbox, element);
			});

			document.querySelector('#emails-view').append(line);

		});

		// If the email has been read, appear it with a gray background
		let read_mail = document.getElementsByClassName("read");
		for (let i = 0; i < read_mail.length; i++) {
	    	read_mail[i].style.backgroundColor = "lightgray";
		}

	});
}

function view_email(mailbox, mail) {
		
	// Show mail itself and hide other views
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'none';
	document.querySelector('#display-email').style.display = 'block';

	// Display email
	document.querySelector('#display-email').innerHTML =
	`<div>From: ${mail.sender} at ${mail.timestamp}</div>`
	+ `<div>Recipients: ${mail.recipients}</div>`
	+ `<div>${mail.subject}</div>`
	+ `<div>${mail.body}</div>`
	+ `<br>`
	+ `<button id="reply" type="button" class="btn btn-primary mr-2">Reply</button>`;

	// Mark email as read
	fetch(`/emails/${mail.id}`, {
		method: "PUT",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify({read: true})
	})
	.then(response => {
		console.log("Success:", response);
	})
	.catch((error) => {
		console.error(error);
	});

	// If mailbox is not sent, display archive/unarchive button
	if (mailbox != "sent") {
		if (!mail.archived) {
			document.querySelector('#display-email').innerHTML += 
			`<button id="archive" type="button" class="btn btn-primary">Archive</button>`;
		} else {
			document.querySelector('#display-email').innerHTML += 
			`<button id="archive" type="button" class="btn btn-primary">Unarchive</button>`;
		}

		document.getElementById("archive").addEventListener('click', () => archive(mail));
		document.getElementById("reply").addEventListener('click', () => reply(mail));
	}

}

function archive(mail) {
	// Update JSON data
	fetch(`/emails/${mail.id}`, {
		method: "PUT",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify({ archived: !mail.archived })
	})
	.then(response => {
		console.log("Success:", response);
		load_mailbox('inbox');
	})
	.catch((error) => {
		console.error(error);
	});
}

function reply(mail) {

	// Show compose view and hide other views
	document.querySelector('#emails-view').style.display = 'none';
	document.querySelector('#display-email').style.display = 'none';
	document.querySelector('#compose-view').style.display = 'block';

	// Pre-fill the form
	document.querySelector('#compose-recipients').value = mail.sender;

	// If subject from begins with "Re:", do not add it again
	if ((mail.subject).substring(0, 3) == "Re:") {
		document.querySelector('#compose-subject').value = mail.subject;
	} else {
		document.querySelector('#compose-subject').value = "Re: " + mail.subject;
	}

	document.querySelector('#compose-body').value = `On ${mail.timestamp} ${mail.sender} wrote: ${mail.body}`;
}

