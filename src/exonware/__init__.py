"""
exonware package - Enterprise-grade Python framework ecosystem
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.8
Generation Date: December 20, 2025
This is a namespace package allowing multiple exonware subpackages
to coexist (xwsystem, xwnode, xwdata, xwauth, etc.)
"""
# Make this a namespace package FIRST

__path__ = __import__('pkgutil').extend_path(__path__, __name__)
