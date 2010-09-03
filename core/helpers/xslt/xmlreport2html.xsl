<?xml version="1.0"?>
<xsl:stylesheet
  version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns="http://www.w3.org/1999/xhtml">

  <xsl:output method="xml" indent="yes" encoding="UTF-8"/>

  <xsl:template match="build">
    <html>
      <head>
        <title>Build Report</title>
      </head>
      <body>
        <h1><xsl:value-of select="@name"/></h1>
        <xsl:apply-templates/>
      </body>
    </html>
  </xsl:template>

  <xsl:template match="plugin">
    <h4><xsl:value-of select="@name"/></h4>
    <ul>
    <xsl:for-each select="step/action">
      <li>
        <code><xsl:value-of select="logdescription"/></code> returned
        <code><xsl:value-of select="returncode"/></code>

        <xsl:choose>
          <xsl:when test="returncode = 0">
            <div style="color: green">
              SUCCESS
            </div>
          </xsl:when>
          <xsl:when test="number(returncode)">
            <div style="color: red">
              FAILED: <code><xsl:value-of select="stderr"/></code>
            </div>
          </xsl:when>
          <xsl:otherwise>
            <div style="color: gray">
              DID NOT FINISHED
            </div>
          </xsl:otherwise>
        </xsl:choose>
      </li>
    </xsl:for-each>
    </ul>
  </xsl:template>

  <xsl:template match="environment">
    <h2><xsl:value-of select="@name"/></h2>
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="configuration">
    <h3><xsl:value-of select="@name"/></h3>
    <xsl:apply-templates/>
  </xsl:template>

</xsl:stylesheet>