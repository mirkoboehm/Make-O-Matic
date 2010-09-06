<?xml version="1.0"?>
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml">

  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

  <xsl:template match="build">
    <html>
      <head>
        <style type="text/css">
body,table {
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
  white-space: pre-wrap;       /* css-3 */
  white-space: -moz-pre-wrap !important;  /* Mozilla, since 1999 */
  white-space: -pre-wrap;      /* Opera 4-6 */
  white-space: -o-pre-wrap;    /* Opera 7 */
  word-wrap: break-word;       /* Internet Explorer 5.5+ */

}
th {
  text-align: left;
}

.success {
  color: green;
}
.fail {
  font-weight: bold;
  color: red;
}
.neutral {
  color: #BBBBBB;
}
        </style>
        <title>Build Report</title>
      </head>
      <body>
        <h1>Build Report for: <xsl:value-of select="@name"/></h1>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="project">
    <h2>Project: <xsl:value-of select="@name"/></h2>
    <span>Build time: <xsl:value-of select="@timing"/></span>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="environment">
    <h2>Environment: <xsl:value-of select="@name"/></h2>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="configuration">
    <h3>Configuration: <xsl:value-of select="@name"/></h3>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="plugin">
    <h4>Plugin: <xsl:value-of select="@name"/></h4>
    <xsl:choose>
      <!-- Plugin templates are inserted here -->
      <xsl:otherwise>
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
              <xsl:apply-templates/>
            </tbody>
          </table>
        </xsl:if>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="plugin/step">
    <tr>
      <td><xsl:value-of select="@name"/></td>
      <td><xsl:value-of select="@timing"/></td>
      <td>
        <xsl:choose>
          <xsl:when test="@failed = 'False'">
            -<!--<span class="success">SUCCESS</span>-->
          </xsl:when>
          <xsl:otherwise>
            <span class="fail">FAILED</span>
          </xsl:otherwise>
        </xsl:choose>
      </td>
    </tr>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="plugin/step/action">
    <tr>
      <td><code><xsl:value-of select="logdescription"/></code></td>
      <td><xsl:value-of select="@timing"/></td>

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
        <span>(returned <code><xsl:value-of select="@returncode"/></code>)</span>
      </td>
    </tr>
    <xsl:if test="number(@returncode) and @returncode != 0">
      <xsl:if test="string-length(stderr) > 0">
        <tr><td colspan="3"><pre><xsl:value-of select="stderr"/></pre></td></tr>
      </xsl:if>
      <xsl:if test="string-length(stdout) > 0">
        <tr><td colspan="3"><pre><xsl:value-of select="stdout"/></pre></td></tr>
      </xsl:if>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
