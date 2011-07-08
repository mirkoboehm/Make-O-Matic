/**
 * Get next *valid* sibling of element
 */
function getNextSibling(startBrother){
	endBrother=startBrother.nextSibling;
	while(endBrother.nodeType!=1){
		endBrother = endBrother.nextSibling;
	}
	return endBrother;
}

/**
 * Getting the closest parent with the given tag name.
 */
function getParentByTagName(obj, tag)
{
	var obj_parent = obj.parentNode;
	if (!obj_parent) return false;
	if (obj_parent.tagName.toLowerCase() == tag) return obj_parent;
	else return getParentByTagName(obj_parent, tag);
}

/**
 * XHTML escaping
 *
 * Replaces & ==> &amp, etc.
 */
function html_escape(string)
{
	return string.replace('&', "&amp;").replace('"', "&quot;").replace("'", "&#39;").replace('>', "&gt;").replace('<', "&lt;");
}

function toggle(obj, style)
{
	var el = obj;
	if ( el.style.display != style ) {
		el.style.display = style;
	}
	else {
		el.style.display = 'none';
	}
}

function load_file(file, viewElement)
{
	// load only once
	if (viewElement.getAttribute("loaded") == "true")
		return;

	// try to fetch file contents when element content is still empty
	var httpRequest = new XMLHttpRequest();
	httpRequest.open("GET", file, true);
	httpRequest.send(null);
	httpRequest.onreadystatechange = function()
	{
		viewElement.innerHTML = html_escape(this.responseText);
		viewElement.setAttribute("loaded", "true");
	}
}

window.onload=function onLoad()
{
}
