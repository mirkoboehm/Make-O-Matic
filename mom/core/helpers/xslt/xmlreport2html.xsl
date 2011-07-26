<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns="http://www.w3.org/1999/xhtml">

	<xsl:output method="xml" indent="yes" encoding="UTF-8" />

	<xsl:param name="summaryOnly"/>
	<xsl:param name="enableCrossLinking"/>

	<xsl:param name="javaScriptContent"/>
	<xsl:param name="cssContent"/>

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
				<script type="text/javascript">
					<xsl:value-of select="$javaScriptContent"/>
				</script>
				<style type="text/css">
					<xsl:value-of select="$cssContent"/>
				</style>
				<title>Build Report for <xsl:value-of select=".//build/@name"/></title>
			</head>
			<body>
				<div id="mom-report">
					<xsl:apply-templates/>
				</div>
			</body>
		</html>
	</xsl:template>

	<xsl:strip-space  elements="*"/>

	<xsl:template match="mom-report">
		<xsl:choose>
			<xsl:when test="$summaryOnly = '1'">
				<xsl:call-template name="showSummary"></xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:apply-templates/>
			</xsl:otherwise>
		</xsl:choose>

	</xsl:template>

	<xsl:template name="showSummary">
		<div class="xheader">
		<xsl:choose>
			<xsl:when test=".//build/@returncode = '0'">
				<xsl:attribute name="style">background-color: #00FF33</xsl:attribute>
				<span class="xsmiley">
					&#9786;
				</span>
				<xsl:value-of select=".//build/@name"/>
				<br/><br/>
				SUCCESS
			</xsl:when>
			<xsl:otherwise>
				<xsl:attribute name="style">background-color: red</xsl:attribute>
				<span class="xsmiley">
					&#9760;
				</span>
				<xsl:value-of select=".//build/@name"/>
				<br/><br/>
				FAILURE
			</xsl:otherwise>
		</xsl:choose>
		</div>

		<table>
			<tr>
				<td width="200px">Status:</td>
				<td>
					<xsl:call-template name="showBuildStatus">
						<xsl:with-param name="returncode" select=".//build/@returncode"/>
					</xsl:call-template>
				</td>
			</tr>
			<tr><td></td><td></td></tr>
			<tr>
				<td>Node:</td>
				<td>
					<xsl:value-of select=".//build/@sys-nodename" />
						[<xsl:value-of select=".//build/@sys-platform" /> (<xsl:value-of select=".//build/@sys-version" />)]
				</td></tr>
		</table>

		<div class="xdetails">
			<xsl:if test="count(.//step[@result = 'Failure']) > 0">
				<h5>Failed steps:</h5>
				<table><tbody>
					<xsl:apply-templates select=".//step[@result = 'Failure']"/>
				</tbody></table>
				<br/>
			</xsl:if>

			<xsl:if test="count(.//exception) > 0">
				<h5>Caught exception:</h5>
				<xsl:apply-templates select=".//exception"/>
			</xsl:if>

			<xsl:if test="count(.//plugin) > 0">
				<h5>Plugin information</h5>
				<table><tbody>
					<xsl:apply-templates select=".//plugin[@pluginType = 'scm']"/>
					<xsl:apply-templates select=".//plugin[@pluginType = 'publisher']"/>
				</tbody></table>
			</xsl:if>
		</div>

		<div class="xfooter">
				Build time: <xsl:value-of select=".//build/@timing" />
		</div>
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
						<th width="40%">Steps: <xsl:value-of select="@name" /></th>
						<th width="20%">Timing</th>
						<th width="40%">Status, Result</th>
					</tr>
				</thead>
				<tbody>
					<xsl:apply-templates />
				</tbody>
			</table>
		</xsl:if>
	</xsl:template>

	<xsl:template match="plugins">
		<xsl:if test="count(./plugin) > 0">
			<table>
			<h5>Plugins:</h5>
			<div class="tag-plugins">
				<xsl:apply-templates/>
			</div>
			</table>
			<br/>
		</xsl:if>
	</xsl:template>

	<xsl:template match="plugin">
		<tr>
		<td>
			<xsl:value-of select="@name" />
			<xsl:if test="@isEnabled = 'False'">
				[Disabled]
			</xsl:if>
			<xsl:if test="@isOptional = 'True'">
				[Optional]
			</xsl:if>
		</td>
		<td>
			<xsl:if test="string-length(objectstatus) > 0">
				(<xsl:value-of select="objectstatus"/>)
				<br/>
			</xsl:if>
		<xsl:if test="$enableCrossLinking = '1' and @relativeLinkTarget != 'None'">
			<a>
				<xsl:attribute name="href">
					<xsl:value-of select="@relativeLinkTarget"/>
				</xsl:attribute>
				<xsl:value-of select="@relativeLinkTargetDescription"/>
			</a>
		</xsl:if>

		<xsl:choose>
			<!-- Plugin templates are inserted here -->
			<xsl:when test="@name = 'placeholder'" />
		</xsl:choose>
		</td>
		</tr>
	</xsl:template>

	<xsl:template match="step">
		<!-- Hide if no actions registered -->
		<xsl:if test="@isEmpty = 'False'">
			<tr>
				<td>
					<span><xsl:value-of select="@name" /></span>

					<span style="float: right;">
					<xsl:if test="$enableCrossLinking = '1' and @relativeLinkTarget != 'None'">
						<a title="Show/hide log" href="javascript:void(0);">
							<xsl:attribute name="onClick">
var logView = getNextSibling(getParentByTagName(this, 'tr'));
load_file('<xsl:value-of select="@relativeLinkTarget"/>', logView.getElementsByTagName('pre')[0]);
toggle(logView, 'table-row');
							</xsl:attribute>
							(+/-)
						</a>

						<a title="Download log file">
							<xsl:attribute name="href">
								<xsl:value-of select="@relativeLinkTarget"/>
							</xsl:attribute>
							(DL)
						</a>
					</xsl:if>
					</span>
				</td>
				<td>
					<xsl:value-of select="@timing" />
				</td>
				<td class="step-status">
					<xsl:call-template name="showStepStatus" />
				</td>
			</tr>
			<tr class="logview" >
				<td colspan="4">
					<pre loaded="false">Not yet loaded.</pre>
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
