let postButton = document.querySelector('#post');
if (postButton) {
	postButton.addEventListener('click', new_post);
}

document.addEventListener('DOMContentLoaded', function() {
	// Default route
	let all_posts = document.querySelector('#all_posts_view');
	if (all_posts) {
		load_all_posts();
	}
	let user_posts = document.querySelector('#user_posts_view');
	if (user_posts) {
		load_user_posts(user_posts.dataset.username);
	}
	let following_posts = document.querySelector('#following_posts_view');
	if (following_posts) {
		load_following_posts();
	}
});

function new_post() {
	let data = {
		content: document.querySelector('#post_content').value
	}

	fetch('/posts', {
		method: "POST",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify(data)
	})
	.then(response => response.json())
	// Check if the fetch is successful
	.then(data => {
		console.log("Success:", data);
		load_all_posts();
	})
	.catch((error) => {
		console.error(error);
	});

	document.querySelector('#post_content').value = "";
}


function like(post_id) {
	// POST request
	let data = {
		post_id: post_id,
		//csrfmiddlewaretoken: document.querySelector('input[name="csrfmiddlewaretoken"]').value
	}

	// Upload JSON data
	fetch('/like_post', {
		method: "POST",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify(data)
	})
	.then(response => response.json())
	.then(data => {
		console.log("Success:", data);
		load_all_posts();
	})
	.catch((error) => {
		console.error(error);
	});
}

function delete_like(like_id) {
	fetch(`/delete_like/${like_id}`, {
		method: "DELETE",
		headers: {
			'Content-type': 'application/json'
		}
	})
	.then(response => response.json())
	.then(data => {
		console.log(data);
		load_all_posts();
	})
	.catch(error => console.log(error))
}

function edit(post_id) {
	let data = {
		content: document.querySelector('#edit_content').value
	}

	fetch(`/edit/${post_id}`, {
		method: "PUT",
		headers: {"Content-type": "application/json; charset=UTF-8"},
		body: JSON.stringify(data)
	})
	.then(response => response.json())
	// Check if the fetch is successful
	.then(data => {
		console.log("Success:", data);
		load_all_posts();
	})
	.catch((error) => {
		console.error(error);
	});
}

function delete_post(post_id) {
	fetch(`/delete_post/${post_id}`, {
		method: "DELETE",
		headers: {
			'Content-type': 'application/json'
		}
	})
	.then(response => response.json())
	.then(data => {
		console.log(data);
		load_all_posts();
	})
	.catch(error => console.log(error))
}

let followButton = document.querySelector('#follow-button')
if (followButton) {
	followButton.addEventListener('click', (event) => {
		event.preventDefault();

		let userId = followButton.dataset["userId"];
		let followed = followButton.dataset["followed"].toLowerCase() === "true";

		fetch(`/follow/${userId}`, {
			method: followed ? "DELETE" : "POST",
			headers: {
				'Content-type': 'application/json'
			}
		})
		.then(response => response.json())
		.then(data => {
			console.log(data);
			followers = document.querySelector('#user-followers');
			followers_count = parseInt(followers.innerHTML);

			followed = !followed;
			followButton.dataset["followed"] = followed;
			followButton.innerHTML = followed ? "Unfollow" : "Follow";
			followers.innerHTML = followed ? (followers_count + 1) : (followers_count - 1);
			followers.innerHTML += " Follower";
		})
		.catch(error => console.log(error))

	});
}

function get_current_page_number() {
	let url = new URL(window.location.href);
	return parseInt(url.searchParams.get("page")) || 1;
}

function load_all_posts() {
	let page = get_current_page_number();
	fetch(`/posts?page=${page}`)
	.then(response => response.json())
	.then(data => {
		load_posts(data, "#all_posts_view");
	});
}

function load_user_posts(username) {
	let page = get_current_page_number();
	fetch(`/posts?username=${username}&page=${page}`)
	.then(response => response.json())
	.then(data => {
		load_posts(data, "#user_posts_view");
	});
}

function load_following_posts(username) {
	let page = get_current_page_number();
	fetch(`/posts?following=true&page=${page}`)
	.then(response => response.json())
	.then(data => {
		load_posts(data, "#following_posts_view");
	});
}

function load_posts(data, htmlPlace) {
	document.querySelector(htmlPlace).innerHTML = "";

	data.posts.forEach(item => {
		let line = document.createElement('div');
		console.log(item);
		let html = `<div class="d-flex justify-content-start single-post my-4">
							<img class="img-fluid user-avatar ms-1 me-3 mt-1" src="${item.user.avatar_url}">
							<div class="single-post-content" id="post-${item.id}">
								<div>
									<a class="username-link" href="/user/${item.user.username}"><strong>${item.user.username}</strong></a>
									<span class="single-post-time ms-1">at ${(item.time).slice(0, 10)}</span>
								</div>
								<div class="mb-1">${item.content}</div>
								<div>
									<a class="like-button" href="#" data-post-id="${item.id}"
									data-was-liked="${item.was_liked}" data-like-id="${item.like_id}"
									data-user-id="${item.user.id}">`;
		if (item.was_liked) {
			html += `<i class="bi bi-heart-fill"></i>`;
		} else {
			html += `<i class="bi bi-heart"></i>`;
		}
			html += `</a><span class="like-count ms-1">${item.like_count}</span>`;

		if (item.is_current) {
			html += `<a class="ms-3 edit" href="#" data-post-content="${item.content}" data-post-id="${item.id}"><i class="bi bi-pencil me-1"></i>Edit</a>
					 <a class="ms-3 delete-post" href="#" data-post-id="${item.id}"><i class="bi bi-trash me-1"></i>Delete</a>`;
		}
		html += `
								</div>
							</div>
							<div class="post-edit-form"></div>
						</div>`;
		line.innerHTML = html;
		document.querySelector(htmlPlace).append(line);

	});

	let pagination = document.querySelector('#pagination');
	if (pagination) {
		pagination.innerHTML = data.pagination;
	}

	let likeButtons = document.querySelectorAll('.like-button');
	if (likeButtons) {
		likeButtons.forEach((element) => {
			element.addEventListener('click', (event) => {
				event.preventDefault();
				let postId = element.dataset['postId'];
				let wasLiked = element.dataset['wasLiked'] === 'true';
				let likeId = element.dataset['likeId'];
				
				if (!wasLiked) {
					like(postId);
				} else {
					delete_like(likeId);
				}
			});
		});
	}

	let editButtons = document.querySelectorAll('.edit');
	if (editButtons) {
		editButtons.forEach((element) => {
			element.addEventListener('click', (event) => {
				event.preventDefault();

				let post_content = element.dataset['postContent'];
				let post_id = element.dataset['postId'];

				document.querySelectorAll('.post-edit-form').forEach(element => element.innerHTML = '');
				document.querySelectorAll('.single-post-content').forEach(element => element.classList.remove('d-none'));

				document.querySelector(`#post-${post_id}`).classList.add('d-none');
				
				document.querySelector(`#post-${post_id} ~ .post-edit-form`).innerHTML = 
				`<div class="my-3">
        			<textarea id="edit_content" class="form-control mb-3" id="floatingTextarea-edit">${post_content}</textarea>
        			<button type="button" class="btn btn-primary save">Save</button>
    			</div>`;

    			let saveButton = document.querySelector('.save');
				if (saveButton) {
					saveButton.addEventListener('click', function() {
						event.preventDefault();
						edit(post_id);
					});
				}
			});
		});
	}

	let deleteButtons = document.querySelectorAll('.delete-post');
	if (deleteButtons) {
		deleteButtons.forEach((element) => {
			element.addEventListener('click', (event) => {
				event.preventDefault();
				let postId = element.dataset['postId'];
				delete_post(postId);
			});
		});
	}
}