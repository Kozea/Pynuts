Additional features
===================

Pynuts provides some javascript tools.


Saving document contenteditable parts
-------------------------------------

If you use Pynuts document class and if you need the `Editable` Pynuts ReST directive in your documents (See here :ref:`api`), you probably want to save the edited contents. Pynuts allows that by using the `save_content` javascript function. It relies on jQuery so you must have imported it before. This function saves your content as simple git files.

How does it work ?
~~~~~~~~~~~~~~~~~~

The `save_content` function uses AJAX in order to save asynchronously a page which contains contenteditable elements by calling the `update_content` method of the document class (See here for more info on `udate_content` :ref:`api`) ; this method returns a JSON containing the document new information like the new commit version. So you don't need to create a route on your application, Pynuts do it for you! You only need to import the source and call the `init_content` function on page loading. Finally just call the save function on any event you want. It will save only if the content has changed until the last save.

Simple example:

.. sourcecode:: html+jinja

  <script src="{{ url_for('_pynuts-static', filename='javascript/save.js') }}"></script>
  <script> $(function () { init_content($(document)); }); </script>
  <button onclick="save_content()"></button>
  <div contenteditable></div>

How the changes are detected ?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Before saving, Pynuts check if the document has changed. How does it work ?

On document load, Pynuts will get all the contenteditable div elements and add a `data-hash` attribute which corresponds to the hashed content of this div element. On calling the save function, Pynuts will compare the current value of the `data-hash` attribute and the current hashed content of the editable div element. If both hash are equals it will call the `unchange_callback`.

What happens on success ?
~~~~~~~~~~~~~~~~~~~~~~~~~~

If the save happened successfuly, Pynuts will automatically change the value of the `data-version` attribute (given by the JSON response of the `update_content` function) and the value of `data-hash` attribute of all the contenteditable div.

Parameters
~~~~~~~~~~

It takes a javascript object as parameter.
The various keys are listed here:
  
`document`: 
  The current document or part of the document containing the contenteditable elements. For example if you have an iframe element, just put `$('iframe')` as value. Default: `$(document)`.
`message`:
  The commit message. Default: `null`.
`author`:
  The commit author. Default: `null`.
`author_email`:
  The commit author email. Default: `null`.
`success_callback`:
  This is the callback function called if the save went well.
`fail_callback`:
  This is the callback function called if the save didn't work properly.
`unchange_callback`:
  This is the callback function called if the content hasn't changed since the last save.

Example:
~~~~~~~~

Here is an detailed example using TeddyBar as text edition toolbar. See `TeddyBar <http://teddybar.org>`_ for more info.

.. sourcecode:: html+jinja

  <script src="{{ url_for('_pynuts-static', filename='javascript/save.js') }}"></script>
  <script>
    $(function () {
        // At page loading, initialize the contenteditable div elements
        init_content($('#page'));
        
        $('#teddybar').teddybar({
            menu: {
                'save': save_button
            },
            commands: {
                save_button: function () {
                    // First, get the commit message
                    message = prompt('Message :');
                    // Then, save
                    save_content({
                        document: $('#page'),
                        message: message,
                        author: "{{ session.get('connected_user') }}",
                        author_email: "{{ session.get('connected_usermail') }}",
                        success_callback: function () {
                            alert('Save went successfully!');
                        },
                        fail_callback: function () {
                            alert('Save failed due to a conflict, please refresh the page.');
                        },
                        unchange_callback: function () {
                            alert('The document hasn't changed.');
                        }
                    });
                }
            }
        });
    });
  <script>
  <section id="page">
    Comments:
    <div contenteditable></div>

    Total: <span contenteditable></span> €
  </section>
