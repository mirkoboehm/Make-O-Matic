<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">

	<xsl:output method="xml" indent="yes" encoding="UTF-8" />

	<xsl:template match="build">
		<html>
			<head>
				<style type="text/css">
body,table {
	font-family: monospace;
	font-size: 9pt;
	width: 1000px;
}
pre {
	font-size: 8pt;
	margin-top: 10px;
	margin-bottom: 10px;
	width: 1000px;
	background-color: #EEEEEE;

	/* line wrap hack */
	white-space: pre-wrap; /* css-3 */
	white-space: -moz-pre-wrap
	!important; /* Mozilla, since 1999 */
	white-space: -pre-wrap; /*
	Opera 4-6 */
	white-space: -o-pre-wrap; /* Opera 7 */
	word-wrap:
	break-word; /* Internet Explorer 5.5+ */

}
th {
	text-align: left;
}

.success {
	color: green;
}
.fail {
	color: red;
}
.neutral {
	color:
	#BBBBBB;
}

.log {
	padding-left: 10px;
}
.step-status {
	font-weight: bold;
}
				</style>
				<title>Build Report</title>
			</head>
			<body>
				<h1>Build Report for: <xsl:value-of select="@name" /></h1>
				<p>
					Platform: <xsl:value-of select="@sys-platform" /> (<xsl:value-of select="@sys-version" />)<br />
					Architecture: <xsl:value-of select="@sys-architecture" /><br />
					Node name: <xsl:value-of select="@sys-nodename" />
				</p>
				<xsl:apply-templates />
			</body>
		</html>
	</xsl:template>

	<xsl:template match="project">
		<h2>Project: <xsl:value-of select="@name" /></h2>
		<!--
		<p>
			Base directory: <xsl:value-of select="@basedir" />
		</p>
		-->
		<p>
			Start time: <xsl:value-of select="@starttime" /><br />
			Stop time : <xsl:value-of select="@stoptime" />
		</p>
		<p>
			Build time:<xsl:value-of select="@timing" />
		</p>
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="environment">
		<h2>Environment: <xsl:value-of select="@name" /></h2>
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="configuration">
		<h3>Configuration: <xsl:value-of select="@name" /></h3>
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="steps">
		<h4>Steps: <xsl:value-of select="@name" /></h4>
		<xsl:if test="count(./step) > 0">
			<table>
				<thead>
					<tr>
						<th width="700px">Instruction</th>
						<th width="200px">Timing</th>
						<th width="300px">Status</th>
					</tr>
				</thead>
				<tbody>
					<xsl:apply-templates />
				</tbody>
			</table>
		</xsl:if>
	</xsl:template>

	<xsl:template match="plugin">
		<h4>Plugin: <xsl:value-of select="@name" /></h4>
		<xsl:choose>
			<!-- Plugin templates are inserted here -->
			<xsl:when test="@name = 'placeholder'" />

			<xsl:otherwise>
				No information about this plugin
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="step">
		<!-- Hide if no actions registered -->
		<xsl:if test="@isEmpty = 'False'">
			<tr>
				<td>
					<xsl:value-of select="@name" />
				</td>
				<td>
					<xsl:value-of select="@timing" />
				</td>
				<td class="step-status">
					<xsl:choose>
						<xsl:when test="@isEnabled = 'False'">
							<span class="neutral">DISABLED</span>
						</xsl:when>
						<xsl:when test="@isEmpty = 'True'">
							<span class="neutral">NO ACTIONS REGISTERED</span>
						</xsl:when>
						<xsl:when test="@failed = 'True'">
							<span class="fail">FAILED</span>
						</xsl:when>
						<xsl:otherwise>
							<span class="success">SUCCESS</span>
						</xsl:otherwise>
					</xsl:choose>
				</td>
			</tr>

			<!-- Only show actions if step has failed -->
			<xsl:if test="@failed = 'True'">
				<xsl:apply-templates />
			</xsl:if>
		</xsl:if>
	</xsl:template>

	<xsl:template match="step/action">
		<tr>
			<td>
				<div class="log">
					<code><xsl:value-of select="logdescription" /></code>
				</div>
			</td>
			<td>
				<xsl:value-of select="@timing" />
			</td>

			<td>
				<xsl:choose>
					<xsl:when test="@returncode = 0">
						<span class="success">
							SUCCESS
						</span>
					</xsl:when>
					<xsl:when test="number(@returncode)">
						<span class="fail">
							FAILED
						</span>
					</xsl:when>
					<xsl:otherwise>
						<span class="neutral">
							DID NOT FINISH
						</span>
					</xsl:otherwise>
				</xsl:choose>
				<span>
					(returned <code><xsl:value-of select="@returncode" /></code>)
				</span>
			</td>
		</tr>
		<!-- Check if action failed, on failure show console output -->
		<xsl:if test="number(@returncode) and @returncode != 0">
			<xsl:if test="string-length(stderr) > 0">
				<tr>
					<td colspan="3">
						<pre>STDERR: <xsl:value-of select="stderr" /></pre>
					</td>
				</tr>
			</xsl:if>
			<xsl:if test="string-length(stdout) > 0">
				<tr>
					<td colspan="3">
						<pre>STDOUT: <xsl:value-of select="stdout" /></pre>
					</td>
				</tr>
			</xsl:if>
		</xsl:if>
	</xsl:template>

</xsl:stylesheet>
