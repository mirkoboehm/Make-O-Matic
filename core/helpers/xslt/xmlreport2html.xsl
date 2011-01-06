<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns="http://www.w3.org/1999/xhtml">

	<xsl:output method="xml" indent="yes" encoding="UTF-8" />

	<xsl:template name="showBuildStatus">
		<xsl:param name="returncode"/>
		<span class="build-status">
			<xsl:choose>
				<xsl:when test="$returncode = 0">
					<span class="success">SUCCESS</span>
				</xsl:when>
				<xsl:when test="$returncode = 1">
					<span class="fail">Build error</span>
				</xsl:when>
				<xsl:when test="$returncode = 2">
					<span class="fail">Configuration error</span>
				</xsl:when>
				<xsl:otherwise>
					<span class="fail">Make-O-Matic error</span>
				</xsl:otherwise>
			</xsl:choose>
		</span>
	</xsl:template>

	<xsl:template name="showStepStatus">
		<xsl:variable name="stepResultClassName">
			<xsl:choose>
				<xsl:when test="@result = 'Success'">
					success
				</xsl:when>
				<xsl:when test="@result = 'NotExecuted'">
					neutral
				</xsl:when>
				<xsl:otherwise>
					fail
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>

		<span class="{$stepResultClassName}">
			<xsl:value-of select="@status"/>,
			<xsl:value-of select="@result"/>
		</span>

	</xsl:template>

	<xsl:template name="showBuildInstructionsStatus">
		<xsl:choose>
			<xsl:when test="@failed = 'True'">
				<span class="fail">FAILED</span>
			</xsl:when>
			<xsl:otherwise>
				<span class="success">SUCCESS</span>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="/">
		<html>
			<head>
				<style type="text/css">
/*** default tags ***/
body, table {
	font-family: Arial;
	width: 800px;
}

div#build-report div {
	margin-left: 1%;
}

pre {
	font-size: 8pt;
	margin-top: 10px;
	margin-bottom: 10px;
	width: 800px;
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

/* headings */
h1 {
	font-size: 120%;
	margin: 0px;
	padding: 0px;
}
h2 {
	font-size: 115%;
}
h3 {
	font-size: 110%;
}
h4 {
	font-size: 105%;
}

h5 {
	margin-top: 5px;
	margin-bottom: 5px;

	font-size: 100%;
}

/*** classes ***/
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
.build-status {
	font-weight: bold;
	font-size: 10pt;
}
.step-status {
	font-weight: bold;
}
				</style>
				<title>Build Report</title>
			</head>
			<body>
				<div id="build-report">
					<xsl:apply-templates/>
				</div>
			</body>
		</html>
	</xsl:template>
	
	<xsl:template match="exception">
		<div class="tag-exception">
			Description: <xsl:value-of select="description"/><br/>
			<pre><xsl:value-of select="traceback"/></pre>
		</div>
	</xsl:template>
	
	<xsl:template match="objectdescription">
		<xsl:if test="string-length(.) > 0">
			<xsl:value-of select="."/>
		</xsl:if>
	</xsl:template>
	
	<xsl:template match="build">
		<h1>Build Report for: <xsl:value-of select="@name" /></h1>
		<div class="tag-build">
			<p>
				Platform: <xsl:value-of select="@sys-platform" /> (<xsl:value-of select="@sys-version" />)<br />
				Architecture: <xsl:value-of select="@sys-architecture" /><br />
				Node name: <xsl:value-of select="@sys-nodename" />
			</p>
			<p class="build-status">
				Build Status:
				<xsl:call-template name="showBuildStatus">
					<xsl:with-param name="returncode" select="@returncode"/>
				</xsl:call-template>
			</p>
			<p>
				Build time: <xsl:value-of select="@timing" />
			</p>
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="project">
		<h2>Project: <xsl:value-of select="@name" /></h2>
		<div class="tag-project">
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="environments">
		<h2>
			Environments: <xsl:value-of select="@name" />
			<xsl:if test="@isOptional = 'True'">
				[Optional]
			</xsl:if>
			<xsl:if test="@isEnabled = 'False'">
				[Disabled]
			</xsl:if>
		</h2>
		<div class="tag-environments">
			<xsl:apply-templates/>
		</div>
	</xsl:template>

	<xsl:template match="environment">
		<h2>Environment: <xsl:value-of select="@name" /> (<xsl:call-template name="showBuildInstructionsStatus"/>)</h2>
		<div class="tag-environment">
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="configuration">
		<h3>Configuration: <xsl:value-of select="@name" /> (<xsl:call-template name="showBuildInstructionsStatus"/>)</h3>
		<div class="tag-configuration">
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="steps">
		<xsl:if test="count(./step) > 0">
			<table>
				<thead>
					<tr>
						<th width="500px">Steps: <xsl:value-of select="@name" /></th>
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

<!--
	<xsl:template match="plugins">
		<xsl:if test="count(./plugin) > 0">
			<h4>Plugins:</h4>
			<div class="tag-plugins">
				<xsl:apply-templates/>
			</div>
		</xsl:if>
	</xsl:template>
-->

	<xsl:template match="plugin">
		<h5>
			<xsl:value-of select="@name" />
			<xsl:if test="@isEnabled = 'False'">
				[Disabled]
			</xsl:if>
			<xsl:if test="@isOptional = 'True'">
				[Optional]
			</xsl:if>
			<xsl:if test="string-length(objectstatus) > 0">
				(<xsl:value-of select="objectstatus"/>)
			</xsl:if>
		</h5>
		<!-- TODO: Doesn't work for some reason, why?
		<div class="tag-plugin">
		 -->
		<xsl:choose>
			<!-- Plugin templates are inserted here -->
			<xsl:when test="@name = 'placeholder'" />
		</xsl:choose>
		<!--</div>-->
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
					<xsl:call-template name="showStepStatus" />
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
